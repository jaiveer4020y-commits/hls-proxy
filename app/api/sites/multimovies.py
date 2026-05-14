from curl_cffi import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote

# Relative imports
from . import gdmirrorbot
from . import utils as u

# We use the Workingg Proxy as the primary entry point to save time
# Adding source=2 directly to help with the bypass
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
        
        # 1. Simplify the Proxy Chain to avoid the 30s Timeout
        # We drop the hls-proxy layer and go directly through workingg
        proxied_url = f"{PROXY_BASE}{quote(url)}"
        
        # 2. Optimized Curl Configuration
        # 'impersonate' adds overhead; 'chrome' is faster than 'chrome120'
        # We set the timeout slightly lower than Vercel's to catch the error gracefully
        response = requests.get(
            proxied_url, 
            timeout=25, 
            impersonate="chrome",
            verify=False # Skip SSL verification to save a few milliseconds
        )
        
        if response.status_code != 200:
            response_data["error"] = f"Proxy Timeout or Block (Status: {response.status_code})"
            return response_data

        html_content = response.text

        # 3. Fast-Extract Player Attributes
        # Regex is significantly faster than BeautifulSoup for large HTML pages
        post_id = re.search(r'data-post=["\'](\d+)["\']', html_content)
        nume = re.search(r'data-nume=["\'](\d+)["\']', html_content)
        dtype = re.search(r'data-type=["\'](movie|tv|episode)["\']', html_content)

        if not (post_id and nume and dtype):
            response_data["error"] = "Target reached, but site is hiding player data (403/Challenge)."
            return response_data
        
        # 4. AJAX POST via Google Proxy
        # We keep this via Google because admin-ajax.php is very sensitive to IP
        ajax_url = f"{domain.rstrip('/')}/wp-admin/admin-ajax.php"
        google_proxy = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"
        
        ajax_payload = {
            "action": "doo_player_ajax",
            "post": post_id.group(1),
            "nume": nume.group(1),
            "type": dtype.group(1)
        }

        ajax_res = requests.post(
            f"{google_proxy}?url={ajax_url}&type=post",
            data=ajax_payload,
            headers={"X-Requested-With": "XMLHttpRequest", "Referer": url},
            timeout=15 # Short timeout for AJAX
        )

        embed_url = ajax_res.json().get("embed_url")

        if not embed_url:
            response_data["error"] = "AJAX finished but no embed link found."
            return response_data

        # 5. Hand-off to GDMirror
        return gdmirrorbot.real_extract(embed_url, request)

    except requests.exceptions.Timeout:
        response_data["error"] = "The connection took too long. Try refreshing."
    except Exception as e:
        response_data["error"] = f"Extraction failed: {str(e)}"

    return response_data
