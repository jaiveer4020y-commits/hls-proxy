from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import re

# Relative imports
from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u

# Your verified working Proxy URL
PROXY_API = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"

def proxy_request(method, target_url, data=None, headers=None):
    """Force all traffic through the Google Apps Script Proxy."""
    proxy_params = {"url": target_url}
    if method.upper() == "POST":
        proxy_params["type"] = "post"
    
    # We use a standard session here because the Proxy handles the TLS
    try:
        if method.upper() == "POST":
            return requests.post(PROXY_API, params=proxy_params, data=data, headers=headers, timeout=25)
        return requests.get(PROXY_API, params=proxy_params, headers=headers, timeout=25)
    except Exception as e:
        print(f"Proxy Request Failed: {e}")
        return None

def real_extract(url, request):
    response_data = {"status": "error", "status_code": 400, "error": None, "servers": []}

    # 1. Force Domain Resolution via Proxy
    domain = u.get_domain(url)
    init_res = proxy_request("GET", domain)
    
    if not init_res or init_res.status_code != 200:
        response_data["error"] = "Proxy could not reach the domain (Blocked even on Google?)."
        return response_data

    # Use the URL returned by the proxy in case of redirects
    actual_domain = u.get_domain(init_res.url) if "script.google.com" not in init_res.url else domain
    target_url = url.replace(domain, actual_domain)

    # 2. Fetch Page via Proxy
    headers = {"Referer": actual_domain, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36"}
    response = proxy_request("GET", target_url, headers=headers)
    
    if not response or "Forbidden" in response.text:
        response_data["error"] = "Target page returned 403 via Proxy. Site may require specific cookies."
        return response_data

    # 3. Parse and Perform AJAX via Proxy
    soup = BeautifulSoup(response.text, "html.parser")
    player = soup.select_one("#player-option-1") or soup.select_one("[data-post]")
    
    if not player:
        response_data["error"] = "Extraction stopped: HTML parsed but player data missing (Check Proxy output)."
        return response_data

    ajax_payload = {
        "action": "doo_player_ajax",
        "post": player.get("data-post"),
        "nume": player.get("data-nume"),
        "type": player.get("data-type")
    }
    
    ajax_url = f"{actual_domain.rstrip('/')}/wp-admin/admin-ajax.php"
    # Note: AJAX MUST be POSTed via Proxy as well
    post_res = proxy_request("POST", ajax_url, data=ajax_payload, headers=headers)

    try:
        res_json = post_res.json()
        embed_url = res_json.get("embed_url")
        
        # 4. Final Hand-off to gdmirrorbot
        # Ensure gdmirrorbot also uses the PROXY_API for its internal calls
        result = gdmirrorbot.real_extract(embed_url, request)
        return result

    except Exception as e:
        response_data["error"] = f"AJAX Proxy Failure: {str(e)}"
        return response_data
