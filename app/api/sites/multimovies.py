from curl_cffi import requests
import re
from urllib.parse import quote
from . import gdmirrorbot
from . import utils as u

GOOGLE_PROXY = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"

def real_extract(url, request):
    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "servers": []
    }

    try:
        domain = u.get_domain(url)

        # Step 1: Fetch page directly with curl_cffi chrome impersonation
        # No proxy needed — curl_cffi TLS fingerprinting bypasses Cloudflare
        stealth_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"{domain}/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        response = requests.get(
            url,
            headers=stealth_headers,
            timeout=25,
            impersonate="chrome124"
        )

        if response.status_code != 200:
            response_data["error"] = f"Site blocked request (Status: {response.status_code})"
            return response_data

        html_content = response.text

        # Step 2: Extract player IDs
        post_match = re.search(r'data-post=["\'](\d+)["\']', html_content)
        nume_match = re.search(r'data-nume=["\'](\d+)["\']', html_content)
        type_match = re.search(r'data-type=["\'](movie|tv|episode)["\']', html_content)

        if not post_match:
            response_data["error"] = "Could not extract player IDs — Cloudflare challenge or page structure changed"
            return response_data

        post = post_match.group(1)
        nume = nume_match.group(1) if nume_match else "1"
        type_ = type_match.group(1) if type_match else "tv"

        # Step 3: Resolve AJAX via Google Proxy
        ajax_url = f"{domain.rstrip('/')}/wp-admin/admin-ajax.php"

        ajax_res = requests.get(
            GOOGLE_PROXY,
            params={
                "type":        "post",
                "url":         ajax_url,
                "action":      "doo_player_ajax",
                "post":        post,
                "nume":        nume,
                "type_value":  type_
            },
            timeout=15,
            impersonate="chrome124"
        )

        data = ajax_res.json()
        embed_url = data.get("embed_url")

        if not embed_url:
            response_data["error"] = f"AJAX returned no embed_url: {data}"
            return response_data

        # Step 4: Hand off to gdmirrorbot
        return gdmirrorbot.real_extract(embed_url, request)

    except Exception as e:
        response_data["error"] = f"Extraction failed: {str(e)}"

    return response_data
