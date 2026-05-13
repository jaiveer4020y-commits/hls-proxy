from curl_cffi import requests
from bs4 import BeautifulSoup
import time

# Use relative imports as per your project structure
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
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Referer": "https://multimovies.fyi/",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# ========================================================
# SESSION (Impersonating Chrome 128)
# =========================================================

# This is the key fix: it mimics a real browser's network handshake
session = requests.Session(impersonate="chrome128")

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
        # 1. Resolve Domain & Handle Challenge
        domain = u.get_domain(url)
        try:
            # First request to solve/bypass verification
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
            response_data["error"] = f"Domain resolution failed: {str(e)}"
            return response_data

        # 2. Fetch the Movie Page
        target_url = url.replace(domain, default_domain)
        page_headers = headers.copy()
        page_headers.update({"Referer": default_domain})

        response = session.get(target_url, headers=page_headers, timeout=20)
        response.raise_for_status()

        # 3. Parse HTML for Player Data
        soup = BeautifulSoup(response.text, "html.parser")
        player_element = soup.select_one("#player-option-1") or soup.select_one("[data-post]")

        if not player_element:
            response_data["error"] = "Player element not found (Still blocked?)."
            return response_data

        post_id = player_element.get("data-post")
        data_type = player_element.get("data-type")
        data_nume = player_element.get("data-nume")

        # 4. AJAX POST for Embed URL
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
            "Origin": default_domain,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })

        post_res = session.post(ajax_url, data=payload, headers=post_headers, timeout=20)
        
        if "application/json" not in post_res.headers.get("Content-Type", ""):
            response_data["error"] = "AJAX blocked by firewall."
            return response_data

        response_json = post_res.json()
        embed_url = response_json.get("embed_url")

        if not embed_url:
            response_data["error"] = "Embed URL missing in response."
            return response_data

        # 5. Process Providers (Streamwish, P2P, etc.)
        media_urls = []
        if response_json.get("type") == "iframe":
            # Using your existing gdmirrorbot logic
            embed_data = gdmirrorbot.real_extract(embed_url, request)
            
            if embed_data.get("status") == "success":
                e_urls = embed_data.get("embed_urls", {})
                for key, val in e_urls.items():
                    if not val: continue
                    l_key = key.lower()
                    
                    if any(x in l_key for x in ["streamwish", "wish", "filelions"]):
                        media_urls.append({"provider": key, "result": streamwish.real_extract(val, request)})
                    elif "p2p" in l_key:
                        media_urls.append({"provider": key, "result": streamp2p.real_extract(val, request)})

        elif response_json.get("type") == "dtshcode":
            sub_soup = BeautifulSoup(embed_url, "html.parser")
            iframe = sub_soup.select_one("iframe")
            if iframe and iframe.get("src"):
                media_urls.append({"provider": "streamwish", "result": streamwish.real_extract(iframe["src"], request)})

        # Final Response
        if not media_urls:
            response_data["error"] = "No playable media found."
            return response_data

        response_data.update({
            "status": "success",
            "status_code": 200,
            "servers": media_urls
        })

    except Exception as e:
        response_data["error"] = f"Extraction failed: {str(e)}"

    return response_data
