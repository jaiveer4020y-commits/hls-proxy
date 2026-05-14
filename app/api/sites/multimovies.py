from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import quote

# Relative imports
from . import gdmirrorbot
from . import utils as u

# Your double-layered proxy endpoint
# This routes through workingg -> hls-proxy -> target
BASE_PROXY = "https://workingg.vercel.app/api/proxy?source=2&url="
HLS_LAYER = "https://hls-proxy.vercel.app/api/?url="

def get_double_proxied_url(target_url):
    """Encodes the target URL into the double-proxy chain."""
    # First, encode the target for the HLS layer
    encoded_target = quote(target_url)
    hls_wrapped = f"{HLS_LAYER}{encoded_target}"
    
    # Second, encode the HLS layer for the workingg layer
    final_wrapped = f"{BASE_PROXY}{quote(hls_wrapped)}"
    return final_wrapped

def real_extract(url, request):
    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "servers": []
    }

    try:
        # 1. Resolve the Domain (Necessary for Referers)
        domain = u.get_domain(url)
        
        # 2. Fetch Movie Page via Double Proxy
        proxied_url = get_double_proxied_url(url)
        
        # We use curl_cffi to maintain a clean TLS handshake even with proxies
        response = requests.get(proxied_url, timeout=30, impersonate="chrome120")
        
        if not response or response.status_code != 200:
            response_data["error"] = f"Double-Proxy failed to reach site (Status: {response.status_code if response else 'Timeout'})"
            return response_data

        html_content = response.text

        # 3. Extract Player Attributes (Post ID, Nume, Type)
        # Using Regex to bypass any BeautifulSoup parsing issues with minified code
        post_id = re.search(r'data-post=["\'](\d+)["\']', html_content)
        nume = re.search(r'data-nume=["\'](\d+)["\']', html_content)
        dtype = re.search(r'data-type=["\'](movie|tv|episode)["\']', html_content)

        if not (post_id and nume and dtype):
            response_data["error"] = "Proxied HTML loaded, but player data-attributes are missing."
            return response_data
        
        p_post = post_id.group(1)
        p_nume = nume.group(1)
        p_type = dtype.group(1)

        # 4. Resolve AJAX via Google Proxy (To handle POST payload)
        # We use Google Apps Script for the AJAX POST because it handles form-data well
        ajax_url = f"{domain.rstrip('/')}/wp-admin/admin-ajax.php"
        google_proxy = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"
        
        ajax_payload = {
            "action": "doo_player_ajax",
            "post": p_post,
            "nume": p_nume,
            "type": p_type
        }

        ajax_res = requests.post(
            f"{google_proxy}?url={ajax_url}&type=post",
            data=ajax_payload,
            headers={"X-Requested-With": "XMLHttpRequest", "Referer": url},
            timeout=20
        )

        res_json = ajax_res.json()
        embed_url = res_json.get("embed_url")

        if not embed_url:
            response_data["error"] = "AJAX response was valid but 'embed_url' was missing."
            return response_data

        # 5. Hand-off to GDMirrorBot
        # IMPORTANT: Ensure your gdmirrorbot.py also uses your proxy for its calls
        return gdmirrorbot.real_extract(embed_url, request)

    except Exception as e:
        response_data["error"] = f"Final Extractor Crash: {str(e)}"
        return response_data
