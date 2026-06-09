import requests
from bs4 import BeautifulSoup

from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u


# =========================================================
# HEADERS
# =========================================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Cache-Control": "max-age=0",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

# Page fetch + AJAX POST proxy
FETCH_PROXY = "https://script.google.com/macros/s/AKfycbw8wVUKZjBoCb_ybTD1q-p4TclYj7PY-SlSDfpHga7Ud7AUXD3i1eZtRowjiNcgPlRDPw/exec"
AJAX_PROXY  = "https://script.google.com/macros/s/AKfycbw8wVUKZjBoCb_ybTD1q-p4TclYj7PY-SlSDfpHga7Ud7AUXD3i1eZtRowjiNcgPlRDPw/exec"

session = requests.Session()


# =========================================================
# MAIN EXTRACTOR
# =========================================================

def real_extract(url, request):

    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "servers": [],
        "debug": []
    }

    if not url:
        response_data["error"] = "No URL provided to extractor."
        return response_data

    try:

        # =================================================
        # Resolve domain
        # =================================================

        domain = u.get_domain(url)
        default_domain = domain

        response_data["debug"].append({
            "step": "resolve_domain",
            "status": "success",
            "default_domain": default_domain
        })

        # =================================================
        # Fetch page
        # =================================================

        target_url = url.replace(domain, default_domain)

        response = session.get(
            FETCH_PROXY,
            params={"type": "fetch", "url": target_url},
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        response_data["debug"].append({
            "step": "fetch_page",
            "status": "success",
            "target_url": target_url
        })

        # =================================================
        # Parse HTML
        # =================================================

        soup = BeautifulSoup(response.text, "html.parser")

        player_element = soup.select_one("#player-option-1")

        if not player_element:
            player_element = soup.select_one("[data-post]")

        if not player_element:
            response_data["error"] = "Player element not found on page."
            return response_data

        response_data["debug"].append({
            "step": "find_player",
            "status": "success"
        })

        # =================================================
        # Extract player data
        # =================================================

        post_id   = player_element.get("data-post")
        data_type = player_element.get("data-type")
        data_nume = player_element.get("data-nume")

        if not all([post_id, data_type, data_nume]):
            response_data["error"] = (
                f"Missing data attributes: "
                f"post={post_id}, "
                f"type={data_type}, "
                f"nume={data_nume}"
            )
            return response_data

        response_data["debug"].append({
            "step": "extract_attributes",
            "status": "success",
            "post": post_id,
            "type": data_type,
            "nume": data_nume
        })

        # =================================================
        # AJAX POST
        # =================================================

        ajax_url = (
            f"{default_domain.rstrip('/')}"
            f"/wp-admin/admin-ajax.php"
        )

        post_res = session.post(
            AJAX_PROXY,
            data={
                "url":    ajax_url,
                "action": "doo_player_ajax",
                "post":   post_id,
                "nume":   data_nume,
                "type":   data_type
            },
            headers=headers,
            timeout=20
        )

        content_type = post_res.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            response_data["error"] = (
                "Site blocked request. "
                f"Expected JSON but got {content_type}. "
                f"Preview: {post_res.text[:200]}"
            )
            return response_data

        try:
            response_json = post_res.json()
        except Exception:
            response_data["error"] = "Server returned invalid JSON."
            return response_data

        response_data["debug"].append({
            "step": "ajax_response",
            "status": "success",
            "response_json": response_json
        })

        if not response_json:
            response_data["error"] = "Empty JSON response."
            return response_data

        # =================================================
        # Get embed URL
        # =================================================

        embed_url = response_json.get("embed_url")

        if not embed_url:
            response_data["error"] = "embed_url missing in AJAX response."
            return response_data

        response_data["debug"].append({
            "step": "embed_url",
            "status": "success",
            "embed_url": embed_url
        })

        media_urls = []

        # =================================================
        # HANDLE IFRAME
        # =================================================

        if response_json.get("type") == "iframe":

            embed_data = gdmirrorbot.real_extract(embed_url, request)

            response_data["debug"].append({
                "step": "gdmirrorbot",
                "result": embed_data
            })

            if not isinstance(embed_data, dict):
                response_data["error"] = "gdmirrorbot returned invalid response."
                return response_data

            if embed_data.get("status") == "error":
                response_data["error"] = (
                    embed_data.get("error")
                    or "gdmirrorbot extractor failed."
                )
                return response_data

            embed_urls = embed_data.get("embed_urls", {})

            response_data["debug"].append({
                "step": "embed_urls",
                "embed_urls": embed_urls
            })

            # =============================================
            # StreamHG / EarnVids — streamwish extractor
            # =============================================

            for sw_key in ["StreamHG", "streamhg", "EarnVids", "earnvids",
                           "FileMoon", "filemoon", "StreamWish", "streamwish"]:
                sw_url = embed_urls.get(sw_key)
                if sw_url:
                    try:
                        sw_res = streamwish.real_extract(
                            sw_url,
                            request
                        )
                        media_urls.append({
                            "provider": sw_key,
                            "result": sw_res
                        })
                    except Exception as e:
                        media_urls.append({
                            "provider": sw_key,
                            "status": "error",
                            "error": str(e)
                        })

            # =============================================
            # RpmShare / UpnShare — streamp2p extractor
            # =============================================

            for p2p_key in ["RpmShare", "UpnShare", "StreamP2p", "rpmhub"]:
                p2p_url = embed_urls.get(p2p_key)
                if p2p_url:
                    try:
                        sp2p_res = streamp2p.real_extract(
                            p2p_url,
                            request
                        )
                        media_urls.append({
                            "provider": p2p_key,
                            "result": sp2p_res
                        })
                    except Exception as e:
                        media_urls.append({
                            "provider": p2p_key,
                            "status": "error",
                            "error": str(e)
                        })

        # =================================================
        # HANDLE DTSHCODE
        # =================================================

        elif response_json.get("type") == "dtshcode":

            sub_soup = BeautifulSoup(embed_url, "html.parser")
            iframe = sub_soup.select_one("iframe")

            if iframe and iframe.get("src"):
                try:
                    sw_res = streamwish.real_extract(
                        iframe["src"],
                        request
                    )
                    media_urls.append({
                        "provider": "streamwish",
                        "result": sw_res
                    })
                except Exception as e:
                    media_urls.append({
                        "provider": "streamwish",
                        "status": "error",
                        "error": str(e)
                    })
            else:
                response_data["error"] = "Could not find iframe inside dtshcode."
                return response_data

        # =================================================
        # NO RESULTS
        # =================================================

        if not media_urls:
            response_data["error"] = {
                "message": "No playable media URLs found",
                "embed_url": embed_url,
                "response_json": response_json,
                "embed_data": (
                    embed_data
                    if 'embed_data' in locals()
                    else None
                )
            }
            return response_data

        # =================================================
        # SUCCESS
        # =================================================

        response_data.update({
            "status": "success",
            "status_code": 200,
            "error": None,
            "servers": media_urls
        })

    except requests.exceptions.Timeout:
        response_data["error"] = "The request timed out."

    except requests.exceptions.RequestException as e:
        response_data["error"] = f"Network Error: {str(e)}"

    except Exception as e:
        response_data["error"] = f"Unexpected Error: {str(e)}"

    return response_data
