import re
import requests
import base64
import json
from urllib.parse import urlparse, parse_qs
from . import site_domains

# Configuration
default_domain = site_domains.get_domain('gdmirrorbot')

PROXY_API = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"

MYSERIES_PROXY = "https://script.google.com/macros/s/AKfycbz8qd16K14o2_lncugE65j7V-WlDWLDogvHcXyT6tdcWQA3SitMqoygzofe4tRnQ4Nbug/exec"

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
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    ),
}

# Create session
session = requests.Session()


# =========================================================
# PARSE EMBED URL
# =========================================================

def _parse_embed_url(url):

    parsed = urlparse(url)

    path_parts = [
        x for x in parsed.path.split("/")
        if x
    ]

    if len(path_parts) < 3:

        raise ValueError(
            f"Unexpected embed URL path format: {parsed.path}"
        )

    embed_type = path_parts[1]

    # =====================================================
    # TV
    # =====================================================

    if embed_type == "tv":

        if len(path_parts) < 5:

            raise ValueError(
                f"Invalid TV embed URL format: {parsed.path}"
            )

        tmdbid = path_parts[2]
        season = path_parts[3]
        episode = path_parts[4]

    # =====================================================
    # MOVIE
    # =====================================================

    elif embed_type == "movie":

        tmdbid = path_parts[2]

        # dummy values for movies
        season = "1"
        episode = "1"

    # =====================================================
    # UNKNOWN
    # =====================================================

    else:

        raise ValueError(
            f"Unsupported embed type: {embed_type}"
        )

    # =====================================================
    # KEY
    # =====================================================

    query_params = parse_qs(parsed.query)

    key_list = query_params.get("key", [])

    if not key_list:

        raise ValueError(
            "Missing 'key' parameter in embed URL"
        )

    key = key_list[0]

    return tmdbid, season, episode, key, embed_type


# =========================================================
# FETCH FILESLUG
# =========================================================

def _fetch_fileslug(
    tmdbid,
    season,
    episode,
    key,
    media_type="tv"
):

    # =====================================================
    # TV
    # =====================================================

    if media_type == "tv":

        params = {
            "tmdbid": tmdbid,
            "season": season,
            "epname": episode,
            "key": key,
        }

    # =====================================================
    # MOVIE
    # =====================================================

    else:

        params = {
            "id": tmdbid,
            "key": key
        }

    response = session.get(
        MYSERIES_PROXY,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("success"):

        raise ValueError(
            f"myseriesapi error: "
            f"{data.get('message', 'Unknown error')}"
        )

    items = data.get("data", [])

    if not items:

        raise ValueError(
            "myseriesapi returned empty data list"
        )

    fileslug = items[0].get("fileslug")

    if not fileslug:

        raise ValueError(
            "fileslug missing in myseriesapi response"
        )

    return fileslug


# =========================================================
# FETCH EMBED DATA
# =========================================================

def _fetch_embed_data(fileslug):

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


# =========================================================
# BUILD IFRAME URLS
# =========================================================

def _build_iframe_urls(embed_data):

    iframe_urls = {}

    mresult = embed_data.get("mresult", "")

    if not mresult:

        raise ValueError(
            "mresult missing or empty in embed data"
        )

    decoded = base64.b64decode(
        mresult
    ).decode("utf-8")

    stream_ids = json.loads(decoded)

    if not stream_ids:

        raise ValueError(
            "mresult decoded to empty"
        )

    site_urls = embed_data.get(
        "siteUrls",
        {}
    )

    friendly_names = embed_data.get(
        "siteFriendlyNames",
        {}
    )

    for provider_key, stream_id in stream_ids.items():

        if not stream_id:
            continue

        base_url = site_urls.get(provider_key)

        if not base_url:
            continue

        name = friendly_names.get(
            provider_key,
            provider_key
        )

        full_url = f"{base_url}{stream_id}"

        iframe_urls[name] = full_url

    return iframe_urls


# =========================================================
# MAIN EXTRACTOR
# =========================================================

def real_extract(url, request):

    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "embed_urls": {}
    }

    try:

        # =================================================
        # Step 1: Parse embed URL
        # =================================================

        tmdbid, season, episode, key, media_type = (
            _parse_embed_url(url)
        )

        # =================================================
        # Step 2: Fetch fileslug
        # =================================================

        fileslug = _fetch_fileslug(
            tmdbid,
            season,
            episode,
            key,
            media_type
        )

        # =================================================
        # Step 3: Fetch embed data
        # =================================================

        embed_data = _fetch_embed_data(
            fileslug
        )

        # =================================================
        # Step 4: Build iframe URLs
        # =================================================

        iframe_urls = _build_iframe_urls(
            embed_data
        )

        if not iframe_urls:

            response_data["error"] = (
                "No stream URLs could be built "
                "from embed data"
            )

            return response_data

        # =================================================
        # SUCCESS
        # =================================================

        response_data["status"] = "success"
        response_data["status_code"] = 200
        response_data["error"] = None
        response_data["embed_urls"] = iframe_urls

    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        response_data["error"] = (
            "[GDMirror] Request timed out"
        )

    # =====================================================
    # REQUEST ERROR
    # =====================================================

    except requests.exceptions.RequestException as e:

        response_data["error"] = (
            f"[GDMirror] HTTP request failed: {str(e)}"
        )

    # =====================================================
    # JSON ERROR
    # =====================================================

    except json.JSONDecodeError as e:

        response_data["error"] = (
            f"[GDMirror] Failed to parse JSON: {str(e)}"
        )

    # =====================================================
    # BASE64 ERROR
    # =====================================================

    except base64.binascii.Error as e:

        response_data["error"] = (
            f"[GDMirror] Failed to decode base64: {str(e)}"
        )

    # =====================================================
    # VALUE ERROR
    # =====================================================

    except ValueError as e:

        response_data["error"] = (
            f"[GDMirror] {str(e)}"
        )

    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        response_data["error"] = (
            f"[GDMirror] Unexpected error: {str(e)}"
        )

    return response_data
