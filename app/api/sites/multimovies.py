from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote

# Relative imports
from . import gdmirrorbot
from . import utils as u

# Primary Proxy
PROXY_BASE = "https://workingg.vercel.app/api/proxy?source=2&url="

def real_extract(url, request):
    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "servers": []
    }

    try:
        domain = u.get_domain(url)
        
        # 1. Stealth Navigation Headers
        # We mimic a user coming directly from the homepage
        stealth_headers = {
            "Authority": domain.replace("https://", ""),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"{domain}/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        # 2. Execute Request through Workingg Proxy
        proxied_url = f"{PROXY_BASE}{quote(url)}"
        
        # Using 'chrome' impersonation for better TLS fingerprinting
        response = requests.get(
            proxied_url, 
            headers=stealth_headers,
            timeout=25, 
            impersonate="chrome"
        )
        
        if response.status_code != 200:
            response_data["error"] = f"Site Blocked Request (Status: {response.status_code})"
            return response_data

        html_content = response.text

        # 3. Extract Player IDs (Regex is safer for challenged HTML)
        # We look for the ID inside the 'doo_player_ajax' pattern specifically
        post_match = re.search(r'data-post=["\'](\d+)["\']', html_content)
        nume_match = re.search(r'data-nume=["\'](\d+)["\']', html_content)
        type_match = re.search(r'data-type=["\'](movie|tv|episode)["\']', html_content)

        if not post_match:
            # If standard regex fails, the site is definitely showing a challenge
            response_data["error"] = "Cloudflare Challenge detected. Proxy IP might be flagged."
            return response_data
        
        # 4. Resolve AJAX via Google Proxy
        # Google IPs are often 'whitelisted' from basic Cloudflare blocks
        ajax_url = f"{domain.rstrip('/')}/wp-admin/admin-ajax.php"
        google_proxy = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"
        
        ajax_payload = {
            "action": "doo_player_ajax",
            "post": post_match.group(1),
            "nume": nume_match.group(1),
            "type": type_match.group(1)
        }

        ajax_res = requests.post(
            f"{google_proxy}?url={ajax_url}&type=post",
            data=ajax_payload,
            headers={
                "X-Requested-With": "XMLHttpRequest", 
                "Referer": url,
                "Origin": domain
            },
            timeout=15
        )

        data = ajax_res.json()
        embed_url = data.get("embed_url")

        if not embed_url:
            response_data["error"] = "AJAX rejected. Check if 'doo_player_ajax' action is still valid."
            return response_data

        # 5. Hand-off to GDMirror for the final provider links
        return gdmirrorbot.real_extract(embed_url, request)

    except Exception as e:
        response_data["error"] = f"Extraction failed: {str(e)}"

    return response_data
