import requests
from bs4 import BeautifulSoup

from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u


# =========================================================
# HEADERS (Full Stealth Configuration)
# =========================================================

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Referer": "https://multimovies.fyi/",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "DNT": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


# =========================================================
# SESSION
# =========================================================

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

        try:
            init_res = session.get(
                domain,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )
            default_domain = u.get_domain(init_res.url)
            response_data["debug"].append({
                "step": "resolve_domain",
                "status": "success",
                "default_domain": default_domain
            })

        except Exception as e:
            response_data["error"] = f"Could not resolve base domain: {str(e)}"
            return response_data

        # =================================================
        # Fetch page
        # =================================================

        target_url = url.replace(domain, default_domain)

        page_headers = headers.copy()
        page_headers.update({
            "Referer": default_domain,
            "Origin": default_domain
        })

        response = session.get(
            target_url,
            headers=page_headers,
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

        ajax_url = f"{default_domain.rstrip('/')}/wp-admin/admin-ajax.php"

        payload = {
            "action": "doo_player_ajax",
            "post":   post_id,
            "nume":   data_nume,
            "type":   data_type
        }

        post_headers = headers.copy()
        post_headers.update({
            "Referer":        target_url,
            "Origin":         default_domain,
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        })

        post_res = session.post(
            ajax_url,
            data=payload,
            headers=post_headers,
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
            # Loop providers
            # =============================================

            for key, value in embed_urls.items():

                if not value:
                    continue

                lower_key = key.lower()

                try:

                    # =====================================
                    # STREAMWISH / FILELIONS
                    # =====================================

                    if any(
                        x in lower_key
                        for x in [
                            "streamwish",
                            "sw",
                            "wish",
                            "filelions",
                            "lion",
                            "dwish",
                            "streamhg",
                            "earnvids",
                            "filemoon",
                            "flmn",
                        ]
                    ):
                        sw_res = streamwish.real_extract(value, request)
                        media_urls.append({
                            "provider": key,
                            "result": sw_res
                        })

                    # =====================================
                    # STREAMP2P
                    # =====================================

                    elif any(
                        x in lower_key
                        for x in [
                            "p2p",
                            "rpmshare",
                            "upnshare",
                            "upnshr",
                            "rpmshre",
                        ]
                    ):
                        sp2p_res = streamp2p.real_extract(value, request)
                        media_urls.append({
                            "provider": key,
                            "result": sp2p_res
                        })

                except Exception as e:
                    media_urls.append({
                        "provider": key,
                        "status": "error",
                        "error": str(e)
                    })

        # =================================================
        # HANDLE DTSHCODE
        # =================================================

        elif response_json.get("type") == "dtshcode":

            sub_soup = BeautifulSoup(embed_url, "html.parser")
            iframe   = sub_soup.select_one("iframe")

            if iframe and iframe.get("src"):
                iframe_src = iframe["src"]
                sw_res = streamwish.real_extract(iframe_src, request)
                media_urls.append({
                    "provider": "streamwish",
                    "result": sw_res
                })
            else:
                response_data["error"] = "Could not find iframe inside dtshcode."
                return response_data

        # =================================================
        # NO RESULTS
        # =================================================

        if not media_urls:
            response_data["error"] = {
                "message":       "No playable media URLs found",
                "embed_url":     embed_url,
                "response_json": response_json,
                "embed_data":    embed_data if 'embed_data' in locals() else None
            }
            return response_data

        # =================================================
        # SUCCESS
        # =================================================

        response_data.update({
            "status":      "success",
            "status_code": 200,
            "error":       None,
            "servers":     media_urls
        })

    except requests.exceptions.Timeout:
        response_data["error"] = "The request timed out."

    except requests.exceptions.RequestException as e:
        response_data["error"] = f"Network Error: {str(e)}"

    except Exception as e:
        response_data["error"] = f"Unexpected Error: {str(e)}"

    return response_data
