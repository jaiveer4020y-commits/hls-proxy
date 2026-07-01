import requests
from bs4 import BeautifulSoup

from . import streamwish, streamp2p
from . import utils as u


# =========================================================
# HEADERS
# =========================================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Cache-Control": "max-age=0",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

API_BASE = "https://streams.iqsmartgames.com/embed"
API_KEY  = "e11a7debaaa4f5d25b671706ffe4d2acb56efbd4"

session = requests.Session()


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

    try:

        # =================================================
        # Case A: a full streams.iqsmartgames.com URL was
        # passed directly as ?url=...
        # =================================================

        if url and "streams.iqsmartgames.com" in url:
            api_url = url

        # =================================================
        # Case B: build the URL from ?id=&type=&s=&e=
        # =================================================

        else:
            tmdb_id    = request.GET.get("id")
            media_type = request.GET.get("type", "movie")   # "movie" or "tv"
            season     = request.GET.get("s")
            episode    = request.GET.get("e")

            if not tmdb_id:
                response_data["error"] = "No TMDB id provided in request."
                return response_data

            if media_type == "tv":
                if not season or not episode:
                    response_data["error"] = "Season and episode required for TV."
                    return response_data
                # https://streams.iqsmartgames.com/embed/tv/{id}/{season}/{episode}?key=...
                api_url = f"{API_BASE}/tv/{tmdb_id}/{season}/{episode}?key={API_KEY}"
            else:
                # https://streams.iqsmartgames.com/embed/movie/{id}?key=...
                api_url = f"{API_BASE}/movie/{tmdb_id}?key={API_KEY}"

        response_data["debug"].append({
            "step": "build_api_url",
            "status": "success",
            "api_url": api_url
        })

        # =================================================
        # Fetch iframe HTML from streams API
        # =================================================

        api_response = session.get(
            api_url,
            headers=headers,
            timeout=20
        )

        api_response.raise_for_status()

        response_data["debug"].append({
            "step": "fetch_streams_api",
            "status": "success"
        })

        # =================================================
        # Parse all iframes from response
        # =================================================

        soup = BeautifulSoup(api_response.text, "html.parser")
        iframes = soup.select("iframe")

        if not iframes:
            response_data["error"] = "No iframes found in API response."
            response_data["debug"].append({
                "step": "parse_iframes",
                "status": "error",
                "raw_html": api_response.text[:500]
            })
            return response_data

        iframe_srcs = [f["src"] for f in iframes if f.get("src")]

        response_data["debug"].append({
            "step": "parse_iframes",
            "status": "success",
            "iframe_srcs": iframe_srcs
        })

        # =================================================
        # Run each iframe through the right extractor
        # =================================================

        media_urls = []

        STREAMWISH_DOMAINS = (
            "streamwish", "filemoon", "streamhg", "earnvids"
        )
        STREAMP2P_DOMAINS = (
            "rpmshare", "upnshare", "streamp2p", "rpmhub"
        )
        PLYR_WRAPPER = "https://plyr.technocosmos.surf/hlsplayer?url="

        for src in iframe_srcs:

            src_lower = src.lower()

            # Unwrap plyr wrapper if present
            if PLYR_WRAPPER in src:
                src = src.split("?url=")[-1]
                src_lower = src.lower()

            try:
                if any(d in src_lower for d in STREAMWISH_DOMAINS):
                    result = streamwish.real_extract(src, request)
                    media_urls.append({
                        "provider": "streamwish",
                        "result": result
                    })

                elif any(d in src_lower for d in STREAMP2P_DOMAINS):
                    result = streamp2p.real_extract(src, request)
                    media_urls.append({
                        "provider": "streamp2p",
                        "result": result
                    })

                else:
                    media_urls.append({
                        "provider": "unknown",
                        "src": src,
                        "status": "skipped"
                    })

            except Exception as e:
                media_urls.append({
                    "provider": src,
                    "status": "error",
                    "error": str(e)
                })

        # =================================================
        # No playable results
        # =================================================

        if not media_urls:
            response_data["error"] = {
                "message": "No playable media URLs found.",
                "iframe_srcs": iframe_srcs
            }
            return response_data

        # =================================================
        # Success
        # =================================================

        response_data.update({
            "status": "success",
            "status_code": 200,
            "error": None,
            "servers": media_urls
        })

    except requests.exceptions.Timeout:
        response_data["error"] = "The request timed out."

    except requests.exceptions.RequestException as e:
        response_data["error"] = f"Network Error: {str(e)}"

    except Exception as e:
        response_data["error"] = f"Unexpected Error: {str(e)}"

    return response_data
