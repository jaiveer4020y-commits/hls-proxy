import requests
import re
import base64
import json
from urllib.parse import urlparse, parse_qs
from . import site_domains

# Configuration
default_domain = site_domains.get_domain('gdmirrorbot')
streamwish_domain = site_domains.get_domain('streamwish')
streamp2p_domain = site_domains.get_domain('streamp2p')

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}

embedhelper_headers = {
    **headers,
    "Content-Type": "application/x-www-form-urlencoded",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://pro.iqsmartgames.com",
    "Host": "pro.iqsmartgames.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

myseriesapi_headers = {
    **headers,
    "Referer": "https://streams.iqsmartgames.com",
    "Host": "streams.iqsmartgames.com",
}

# Create session
session = requests.Session()


def _parse_embed_url(url):
    """
    Parse embed URL to extract tmdbid, season, episode, key.
    Expected format: /embed/tv/{tmdbid}/{season}/{episode}?key=xxx
    """
    parsed = urlparse(url)
    path_parts = parsed.path.rstrip("/").split("/")
    # path_parts: ['', 'embed', 'tv', '{tmdbid}', '{season}', '{episode}']
    
    if len(path_parts) < 6:
        raise ValueError(f"Unexpected embed URL path format: {parsed.path}")
    
    tmdbid  = path_parts[-3]
    season  = path_parts[-2]
    episode = path_parts[-1]
    
    query_params = parse_qs(parsed.query)
    key_list = query_params.get("key", [])
    if not key_list:
        raise ValueError("Missing 'key' parameter in embed URL")
    key = key_list[0]
    
    return tmdbid, season, episode, key


def _fetch_fileslug(tmdbid, season, episode, key):
    """
    Step 1: GET myseriesapi to get fileslug from tmdbid/season/episode/key.
    Returns fileslug string or raises Exception.
    """
    response = session.get(
        "https://streams.iqsmartgames.com/myseriesapi",
        params={
            "tmdbid": tmdbid,
            "season": season,
            "epname": episode,
            "key": key,
        },
        headers=myseriesapi_headers,
        timeout=15
    )
    response.raise_for_status()
    
    data = response.json()
    
    if not data.get("success"):
        raise ValueError(f"myseriesapi error: {data.get('message', 'Unknown error')}")
    
    items = data.get("data", [])
    if not items:
        raise ValueError("myseriesapi returned empty data list")
    
    fileslug = items[0].get("fileslug")
    if not fileslug:
        raise ValueError("fileslug missing in myseriesapi response")
    
    return fileslug


def _fetch_stream_keys(fileslug):
    """
    Step 2: POST embedhelper.php with sid=fileslug.
    Returns decoded JSON with stream keys or raises Exception.
    """
    response = session.post(
        "https://pro.iqsmartgames.com/embedhelper.php",
        data={"sid": fileslug},
        headers=embedhelper_headers,
        timeout=15
    )
    response.raise_for_status()
    
    embed_json = response.json()
    
    if "mresult" not in embed_json:
        raise ValueError("No 'mresult' field in embedhelper response")
    
    decoded = base64.b64decode(embed_json["mresult"]).decode("utf-8")
    stream_data = json.loads(decoded)
    
    return stream_data


def _build_iframe_urls(stream_data):
    """
    Step 3: Build iframe URLs from stream keys.
    Returns dict of provider -> url.
    """
    iframe_urls = {}
    
    if "smwh" in stream_data:
        iframe_urls["streamwish"] = f"{streamwish_domain}/e/{stream_data['smwh']}"
    
    if "strmp2" in stream_data:
        iframe_urls["streamp2p"] = f"{streamp2p_domain}/#{stream_data['strmp2']}"
    
    return iframe_urls


def real_extract(url, request):
    """
    Main extractor. Extracts streaming URLs from iqsmartgames embed URL.
    
    Flow:
      1. Parse embed URL → tmdbid, season, episode, key
      2. GET myseriesapi → fileslug
      3. POST embedhelper.php with sid=fileslug → base64 stream keys
      4. Decode and build final iframe URLs
    
    Returns dict:
      {
        'status': 'success' | 'error',
        'status_code': 200 | 400,
        'error': None | str,
        'embed_urls': {} | {'streamwish': '...', 'streamp2p': '...'}
      }
    """
    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "embed_urls": {}
    }

    try:
        # Step 1: Parse embed URL
        tmdbid, season, episode, key = _parse_embed_url(url)

        # Step 2: Fetch fileslug from myseriesapi
        fileslug = _fetch_fileslug(tmdbid, season, episode, key)

        # Step 3: Fetch stream keys from embedhelper
        stream_data = _fetch_stream_keys(fileslug)

        # Step 4: Build iframe URLs
        iframe_urls = _build_iframe_urls(stream_data)

        if not iframe_urls:
            response_data["error"] = "No supported stream keys found (smwh/strmp2 missing)"
            return response_data

        # Success
        response_data["status"] = "success"
        response_data["status_code"] = 200
        response_data["error"] = None
        response_data["embed_urls"] = iframe_urls

    except requests.exceptions.Timeout:
        response_data["error"] = "[GDMirror] Request timed out"
    except requests.exceptions.RequestException as e:
        response_data["error"] = f"[GDMirror] HTTP request failed: {str(e)}"
    except json.JSONDecodeError as e:
        response_data["error"] = f"[GDMirror] Failed to parse JSON: {str(e)}"
    except base64.binascii.Error as e:
        response_data["error"] = f"[GDMirror] Failed to decode base64: {str(e)}"
    except ValueError as e:
        response_data["error"] = f"[GDMirror] {str(e)}"
    except Exception as e:
        response_data["error"] = f"[GDMirror] Unexpected error: {str(e)}"

    return response_data
