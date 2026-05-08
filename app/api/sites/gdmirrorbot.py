import re
import requests
import base64
import json
from urllib.parse import urlparse, parse_qs
from . import site_domains

# Configuration
default_domain = site_domains.get_domain('gdmirrorbot')

# API Endpoints
PROXY_API = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"
MYSERIES_PROXY = "https://script.google.com/macros/s/AKfycbz8qd16K14o2_lncugE65j7V-WlDWLDogvHcXyT6tdcWQA3SitMqoygzofe4tRnQ4Nbug/exec"

# Movie specific endpoint based on your example
MYMOVIE_API_BASE = "https://streams.iqsmartgames.com/mymovieapi"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://multimovies.fyi/"
}

session = requests.Session()

# =========================================================
# STEP 1: PARSE THE INCOMING URL
# =========================================================
def _parse_embed_url(url):
    parsed = urlparse(url)
    path_parts = [x for x in parsed.path.split("/") if x]
    query_params = parse_qs(parsed.query)
    
    key = query_params.get("key", [None])[0]
    if not key:
        raise ValueError("Missing 'key' parameter in embed URL")

    # Detect Movie vs TV
    # URL format: /embed/movie/tt33014583 or /embed/tv/ID/S/E
    embed_type = path_parts[1] if len(path_parts) > 1 else "unknown"

    if embed_type == "movie":
        return path_parts[2], "1", "1", key, "movie"
    elif embed_type == "tv":
        return path_parts[2], path_parts[3], path_parts[4], key, "tv"
    else:
        raise ValueError(f"Unsupported embed type: {embed_type}")

# =========================================================
# STEP 2: FETCH FILESLUG (Handling Movie vs TV Endpoints)
# =========================================================
def _fetch_fileslug(tmdbid, season, episode, key, media_type):
    if media_type == "tv":
        # Use your Google Apps Script Proxy for Series
        params = {"tmdbid": tmdbid, "season": season, "epname": episode, "key": key}
        target_url = MYSERIES_PROXY
    else:
        # Use the direct Movie API endpoint or route it through a proxy if needed
        # Based on your example: mymovieapi?imdbid=tt...&key=...
        params = {"imdbid": tmdbid, "key": key}
        # We route this through your PROXY_API to avoid Vercel IP blocks
        target_url = f"{PROXY_API}?url={MYMOVIE_API_BASE}"

    response = session.get(target_url, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise ValueError(f"API Error: {data.get('message', 'No results found')}")

    items = data.get("data", [])
    if not items:
        raise ValueError("API returned empty data list")

    fileslug = items[0].get("fileslug")
    if not fileslug:
        raise ValueError("fileslug missing in response")

    return fileslug

# =========================================================
# STEP 3 & 4: FETCH DATA & BUILD URLS
# =========================================================
def _fetch_embed_data(fileslug):
    # This always goes to the embedhelper via PROXY_API
    response = session.get(
        PROXY_API,
        params={
            "type": "post",
            "post_sid": fileslug,
            "url": "https://pro.iqsmartgames.com/embedhelper.php"
        },
        headers=headers,
        timeout=20
    )
    response.raise_for_status()
    return response.json()

def _build_iframe_urls(embed_data):
    iframe_urls = {}
    mresult = embed_data.get("mresult", "")
    if not mresult:
        return {}

    decoded = base64.b64decode(mresult).decode("utf-8")
    stream_ids = json.loads(decoded)

    # CRITICAL: Handle if stream_ids is a List instead of a Dict
    if isinstance(stream_ids, list):
        # If it's an empty list [], it will simply skip this
        for item in stream_ids:
            if isinstance(item, dict):
                for k, v in item.items():
                    _map_url(iframe_urls, k, v, embed_data)
    elif isinstance(stream_ids, dict):
        for k, v in stream_ids.items():
            _map_url(iframe_urls, k, v, embed_data)

    return iframe_urls

def _map_url(iframe_urls, pk, sid, embed_data):
    if not sid: return
    base_url = embed_data.get("siteUrls", {}).get(pk)
    if base_url:
        name = embed_data.get("siteFriendlyNames", {}).get(pk, pk)
        iframe_urls[name] = f"{base_url}{sid}"

# =========================================================
# MAIN ENTRY POINT
# =========================================================
def real_extract(url, request):
    response_data = {"status": "error", "status_code": 400, "error": None, "embed_urls": {}}
    try:
        tmdbid, season, episode, key, media_type = _parse_embed_url(url)
        
        fileslug = _fetch_fileslug(tmdbid, season, episode, key, media_type)
        
        embed_data = _fetch_embed_data(fileslug)
        
        iframe_urls = _build_iframe_urls(embed_data)

        if not iframe_urls:
            response_data["error"] = "Extraction finished but no playable servers were found."
        else:
            response_data.update({"status": "success", "status_code": 200, "embed_urls": iframe_urls})

    except Exception as e:
        response_data["error"] = f"[GDMirror] {str(e)}"

    return response_data
