import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u


# =========================================================
# HEADERS
# =========================================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}

FETCH_PROXY  = "https://script.google.com/macros/s/AKfycbzwlgaq7IkI4NkLokhTcL7zxf-aiD9GZB0S4grtOuNofuw-Yzr3pmKX_6uhit4IQx8Y/exec"


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
                FETCH_PROXY,
                params={
                    "type": "fetch",
                    "url": domain
                },
                headers=headers,
                timeout=15,
                allow_redirects=True
            )

            default_domain = domain

            response_data["debug"].append({
                "step": "resolve_domain",
                "status": "success",
                "default_domain": default_domain
            })

        except Exception as e:
            response_data["error"] = f"Could not resolve base domain: {str(e)}"
            return response_data

        # =================================================
        # Fetch page via Proxy
        # =================================================
        target_url = url.replace(domain, default_domain)

        response = session.get(
            FETCH_PROXY,
            params={
                "type": "fetch",
                "url": target_url
            },
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

        player_element = soup.select_one("#player-option-1") or soup.select_one("[data-post]")

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
            response_data["error"] = f"Missing data: post={post_id}, type={data_type}, nume={data_nume}"
            return response_data

        response_data["debug"].append({
            "step": "extract_attributes",
            "status": "success",
            "post": post_id,
            "type": data_type,
            "nume": data_nume
        })

        # =================================================
        # AJAX POST via Proxy (FIXED)
        # =================================================
        ajax_url = f"{default_domain.rstrip('/')}/wp-admin/admin-ajax.php"

        payload = {
            "action": "doo_player_ajax",
            "post": post_id,
            "nume": data_nume,
            "type": data_type
        }

        post_headers = headers.copy()
        post_headers.update({
            "Referer": target_url,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
        })

        # We route the POST through the FETCH_PROXY to bypass Cloudflare
        post_res = session.post(
            FETCH_PROXY,
            params={
                "type": "fetch",
                "url": ajax_url
            },
            data=payload,
            headers=post_headers,
            timeout=20
        )

        content_type = post_res.headers.get("Content-Type", "")

        # If the proxy returns the "Just a moment" page, content_type is text/html
        if "application/json" not in content_type and "text/javascript" not in content_type:
            response_data["error"] = (
                "Site blocked request. "
                f"Expected JSON but got {content_type}. "
                f"Preview: {post_res.text[:100]}"
            )
            return response_data

        try:
            response_json = post_res.json()
        except Exception:
            # Fallback if proxy returns JSON as string
            try:
                import json
                response_json = json.loads(post_res.text)
            except:
                response_data["error"] = "Server returned invalid JSON."
                return response_data

        response_data["debug"].append({
            "step": "ajax_response",
            "status": "success"
        })

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
            
            if isinstance(embed_data, dict) and embed_data.get("status") == "success":
                embed_urls = embed_data.get("embed_urls", {})
                for key, value in embed_urls.items():
                    if not value: continue
                    lower_key = key.lower()
                    try:
                        if any(x in lower_key for x in ["streamwish", "sw", "wish", "filelions", "lion"]):
                            media_urls.append({"provider": key, "result": streamwish.real_extract(value, request)})
                        elif "p2p" in lower_key:
                            media_urls.append({"provider": key, "result": streamp2p.real_extract(value, request)})
                    except Exception as e:
                        media_urls.append({"provider": key, "status": "error", "error": str(e)})

        # =================================================
        # HANDLE DTSHCODE
        # =================================================
        elif response_json.get("type") == "dtshcode":
            sub_soup = BeautifulSoup(embed_url, "html.parser")
            iframe = sub_soup.select_one("iframe")
            if iframe and iframe.get("src"):
                sw_res = streamwish.real_extract(iframe["src"], request)
                media_urls.append({"provider": "streamwish", "result": sw_res})

        if not media_urls:
            response_data["error"] = "No playable media URLs found"
            return response_data

        response_data.update({
            "status": "success",
            "status_code": 200,
            "servers": media_urls
        })

    except Exception as e:
        response_data["error"] = f"Unexpected Error: {str(e)}"

    return response_data
