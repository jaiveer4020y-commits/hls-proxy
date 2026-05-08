import re
import requests
import base64
import json
from urllib.parse import urlparse, parse_qs
from . import site_domains

# =========================================================
# CONFIG
# =========================================================

default_domain = site_domains.get_domain('gdmirrorbot')

PROXY_API = (
    "https://script.google.com/macros/s/"
    "AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"
)

MYSERIES_PROXY = (
    "https://script.google.com/macros/s/"
    "AKfycbz8qd16K14o2_lncugE65j7V-WlDWLDogvHcXyT6tdcWQA3SitMqoygzofe4tRnQ4Nbug/exec"
)

headers = {
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,image/apng,*/*;q=0.8"
    ),
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

# =========================================================
# SESSION
# =========================================================

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
            f"Unexpected embed URL format: {parsed.path}"
        )

    embed_type = path_parts[1]

    # =====================================================
    # TV
    # =====================================================

    if embed_type == "tv":

        if len(path_parts) < 5:

            raise ValueError(
                f"Invalid TV embed format: {parsed.path}"
            )

        media_type = "tv"

        media_id = path_parts[2]
        season = path_parts[3]
        episode = path_parts[4]

    # =====================================================
    # MOVIE
    # =====================================================

    elif embed_type == "movie":

        media_type = "movie"

        media_id = path_parts[2]

        season = None
        episode = None

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

    key = query_params.get("key", [None])[0]

    if not key:

        raise ValueError(
            "Missing key parameter"
        )

    return {
        "media_type": media_type,
        "media_id": media_id,
        "season": season,
        "episode": episode,
        "key": key
    }


# =========================================================
# FETCH FILESLUG
# =========================================================

def _fetch_fileslug(parsed_data):

    media_type = parsed_data["media_type"]

    # =====================================================
    # TV API
    # =====================================================

    if media_type == "tv":

        response = session.get(
            MYSERIES_PROXY,
            params={
                "tmdbid": parsed_data["media_id"],
                "season": parsed_data["season"],
                "epname": parsed_data["episode"],
                "key": parsed_data["key"]
            },
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
                "myseriesapi returned empty data"
            )

        fileslug = items[0].get("fileslug")

        if not fileslug:

            raise ValueError(
                "fileslug missing in TV response"
            )

        return fileslug

    # =====================================================
    # MOVIE API
    # =====================================================

    movie_url = (
        "https://streams.iqsmartgames.com/mymovieapi"
    )

    response = session.get(
        movie_url,
        params={
            "imdbid": parsed_data["media_id"],
            "key": parsed_data["key"]
        },
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("success"):

        raise ValueError(
            f"mymovieapi error: "
            f"{data.get('message', 'Unknown error')}"
        )

    items = data.get("data", [])

    if not items:

        raise ValueError(
            "mymovieapi returned empty data"
        )

    fileslug = items[0].get("fileslug")

    if not fileslug:

        raise ValueError(
            "fileslug missing in movie response"
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
            "url": (
                "https://pro.iqsmartgames.com/"
                "embedhelper.php"
            )
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

    mresult = embed_data.get("mresult")

    if not mresult:

        raise ValueError(
            "mresult missing in embed data"
        )

    decoded = base64.b64decode(
        mresult
    ).decode("utf-8")

    stream_ids = json.loads(decoded)

    if not stream_ids:

        raise ValueError(
            "Decoded mresult is empty"
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

        provider_name = friendly_names.get(
            provider_key,
            provider_key
        )

        iframe_urls[provider_name] = (
            f"{base_url}{stream_id}"
        )

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
        # STEP 1
        # Parse URL
        # =================================================

        parsed_data = _parse_embed_url(url)

        # =================================================
        # STEP 2
        # Get fileslug
        # =================================================

        fileslug = _fetch_fileslug(
            parsed_data
        )

        # =================================================
        # STEP 3
        # Fetch embed data
        # =================================================

        embed_data = _fetch_embed_data(
            fileslug
        )

        # =================================================
        # STEP 4
        # Build stream URLs
        # =================================================

        iframe_urls = _build_iframe_urls(
            embed_data
        )

        if not iframe_urls:

            response_data["error"] = (
                "No playable stream URLs found"
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
            f"[GDMirror] JSON parse failed: {str(e)}"
        )

    # =====================================================
    # BASE64 ERROR
    # =====================================================

    except base64.binascii.Error as e:

        response_data["error"] = (
            f"[GDMirror] Base64 decode failed: {str(e)}"
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
