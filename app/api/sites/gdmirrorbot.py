import requests
import base64
import json
from urllib.parse import urlparse, parse_qs
from . import site_domains

# Configuration
default_domain = site_domains.get_domain('gdmirrorbot')

PROXY_API = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"

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

myseries_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Cache-Control": "max-age=0",
    "Connection": "Keep-Alive",
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
    Step 1: GET myseriesapi to get fileslug.
    """
    response = session.get(
        "https://streams.iqsmartgames.com/myseriesapi",
        params={
            "tmdbid": tmdbid,
            "season": season,
            "epname": episode,
            "key": key,
        },
        headers=myseries_headers,
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


def _fetch_embed_data(fileslug):
    """
    Step 2: POST embedhelper.php via proxy with plain sid (no curly braces).
    Returns full response JSON.
    """
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
    """
    Step 3: Decode mresult base64 JSON to get stream IDs,
    then combine with siteUrls to build final URLs.

    mresult decodes to e.g.:
    {
      "smwh": "n2pwiubil1oz",
      "strmp2": "vieug6",
      "flls": "mgugmtbjupw1",
      "rpmshre": "bffhig",
      "upnshr": "mhlhax",
      ...
    }
    """
    iframe_urls = {}

    # Decode mresult → stream IDs
    mresult = embed_data.get("mresult", "")
    if not mresult:
        raise ValueError("mresult missing or empty in embed data")

    decoded = base64.b64decode(mresult).decode("utf-8")
    stream_ids = json.loads(decoded)

    if not stream_ids:
        raise ValueError("mresult decoded to empty — check fileslug is correct")

    site_urls      = embed_data.get("siteUrls", {})
    friendly_names = embed_data.get("siteFriendlyNames", {})

    for provider_key, stream_id in stream_ids.items():
        if not stream_id:
            continue

        base_url = site_urls.get(provider_key)
        if not base_url:
            continue

        name     = friendly_names.get(provider_key, provider_key)
        full_url = f"{base_url}{stream_id}"
        iframe_urls[name] = full_url

    return iframe_urls


def real_extract(url, request):
    """
    Main extractor. Extracts streaming URLs from iqsmartgames embed URL.

    Flow:
      1. Parse embed URL → tmdbid, season, episode, key
      2. GET myseriesapi → fileslug
      3. POST embedhelper.php via proxy with sid=fileslug
      4. Decode mresult base64 → stream IDs + combine with siteUrls

    Returns dict:
      {
        'status': 'success' | 'error',
        'status_code': 200 | 400,
        'error': None | str,
        'embed_urls': {} | {'StreamHG': '...', 'StreamP2p': '...', ...}
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

        # Step 3: Fetch embed data via proxy
        embed_data = _fetch_embed_data(fileslug)

        # Step 4: Build iframe URLs from mresult
        iframe_urls = _build_iframe_urls(embed_data)

        if not iframe_urls:
            response_data["error"] = "No stream URLs could be built from embed data"
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
