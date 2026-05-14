from curl_cffi import requests
from bs4 import BeautifulSoup
import time
import json

# Relative imports
from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u

# =========================================================
# HEADERS (Enhanced Stealth)
# =========================================================
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
}

PROXY_API = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"

# Use Impersonate for TLS Fingerprinting (Bypasses basic Cloudflare)
session = requests.Session(impersonate="chrome120")

def get_html_stealth(url, current_headers):
    """Try direct impersonation first, fallback to Proxy if 403 occurs."""
    try:
        res = session.get(url, headers=current_headers, timeout=15)
        if res.status_code == 403:
            # Fallback to Google Proxy if Vercel IP is blocked
            proxy_url = f"{PROXY_API}?url={url}"
            res = session.get(proxy_url, headers=current_headers, timeout=20)
        return res
    except Exception:
        return None

def real_extract(url, request):
    response_data = {
        "status": "error", "status_code": 400, "error": None,
        "servers": [], "debug": []
    }

    try:
        # 1. Resolve Domain
        domain = u.get_domain(url)
        init_res = get_html_stealth(domain, COMMON_HEADERS)
        
        if not init_res or init_res.status_code != 200:
            response_data["error"] = f"Site is blocking extraction (Status: {init_res.status_code if init_res else 'Timeout'})"
            return response_data

        default_domain = u.get_domain(init_res.url)
        target_url = url.replace(domain, default_domain)

        # 2. Fetch Movie Page
        page_headers = COMMON_HEADERS.copy()
        page_headers.update({"Referer": default_domain})
        response = get_html_stealth(target_url, page_headers)
        
        if not response:
            response_data["error"] = "Failed to fetch movie page content."
            return response_data

        # 3. Parse Player Data
        soup = BeautifulSoup(response.text, "html.parser")
        player_element = soup.select_one("#player-option-1") or soup.select_one("[data-post]")

        if not player_element:
            response_data["error"] = "Player element not found. Site may have changed layout."
            return response_data

        payload = {
            "action": "doo_player_ajax",
            "post": player_element.get("data-post"),
            "nume": player_element.get("data-nume"),
            "type": player_element.get("data-type")
        }

        # 4. AJAX POST (Must look like an XHR request)
        ajax_url = f"{default_domain.rstrip('/')}/wp-admin/admin-ajax.php"
        ajax_headers = COMMON_HEADERS.copy()
        ajax_headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": target_url,
            "Origin": default_domain
        })

        # POST requests usually need to be routed through proxy too if 403 is persistent
        post_res = session.post(ajax_url, data=payload, headers=ajax_headers, timeout=15)
        
        # If AJAX is blocked, try routing the POST via Proxy as well
        if post_res.status_code == 403:
            proxy_ajax = f"{PROXY_API}?url={ajax_url}&type=post"
            post_res = session.post(proxy_ajax, data=payload, headers=ajax_headers)

        res_json = post_res.json()
        embed_url = res_json.get("embed_url")

        # 5. Handle Providers
        media_urls = []
        if res_json.get("type") == "iframe":
            # Pass to your updated gdmirrorbot (which now handles movies vs tv)
            embed_data = gdmirrorbot.real_extract(embed_url, request)
            
            if embed_data.get("status") == "success":
                for key, val in embed_data.get("embed_urls", {}).items():
                    l_key = key.lower()
                    if any(x in l_key for x in ["streamwish", "wish", "filelions"]):
                        media_urls.append({"name": key, "url": val, "handler": "streamwish"})
                    elif "p2p" in l_key:
                        media_urls.append({"name": key, "url": val, "handler": "streamp2p"})
        
        elif "iframe" in embed_url: # Case for dtshcode
            match = re.search(r'src=["\'](.*?)["\']', embed_url)
            if match:
                media_urls.append({"name": "Primary", "url": match.group(1), "handler": "streamwish"})

        if not media_urls:
            response_data["error"] = "No playable servers found after AJAX resolution."
            return response_data

        response_data.update({
            "status": "success", "status_code": 200,
            "servers": media_urls
        })

    except Exception as e:
        response_data["error"] = f"Critical Error: {str(e)}"

    return response_data
