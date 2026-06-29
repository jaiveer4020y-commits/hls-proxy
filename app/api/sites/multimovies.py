import requests
from bs4 import BeautifulSoup

from . import streamwish, gdmirrorbot, streamp2p, site_domains
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
        # Build API URL from request params
        # =================================================

        tmdb_id    = request.get("id")
        media_type = request.get("type", "movie")   # "movie" or "tv"
        season     = request.get("s")
        episode    = request.get("e")

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
        # HANDLE IFRAME
        # =================================================

        if response_json.get("type") == "iframe":

            embed_data = gdmirrorbot.real_extract(embed_url, request)

            response_data["debug"].append({
                "step": "gdmirrorbot",
                "result": embed_data
            })

            if not isinstance(embed_data, dict):
                response_data["error"] = "gdmirrorbot returned invalid response."
                return response_data

            if embed_data.get("status") == "error":
                response_data["error"] = (
                    embed_data.get("error")
                    or "gdmirrorbot extractor failed."
                )
                return response_data

            embed_urls = embed_data.get("embed_urls", {})

            response_data["debug"].append({
                "step": "embed_urls",
                "embed_urls": embed_urls
            })

            # =============================================
            # StreamHG / EarnVids — streamwish extractor
            # =============================================

            for sw_key in [
                "StreamHG", "streamhg",
                "EarnVids", "earnvids",
                "FileMoon", "filemoon",
                "StreamWish", "streamwish"
            ]:
                sw_url = embed_urls.get(sw_key)
                if sw_url:
                    try:
                        sw_res = streamwish.real_extract(
                            sw_url,
                            request
                        )
                        media_urls.append({
                            "provider": sw_key,
                            "result": sw_res
                        })
                    except Exception as e:
                        media_urls.append({
                            "provider": sw_key,
                            "status": "error",
                            "error": str(e)
                        })

            # =============================================
            # RpmShare / UpnShare — streamp2p extractor
            # =============================================

            for p2p_key in [
                "RpmShare", "UpnShare",
                "StreamP2p", "rpmhub"
            ]:
                p2p_url = embed_urls.get(p2p_key)
                if p2p_url:
                    # Unwrap plyr wrapper if present
                    if "https://plyr.technocosmos.surf/hlsplayer?url=" in p2p_url:
                        p2p_url = p2p_url.split("?url=")[-1]
                    try:
                        sp2p_res = streamp2p.real_extract(
                            p2p_url,
                            request
                        )
                        media_urls.append({
                            "provider": p2p_key,
                            "result": sp2p_res
                        })
                    except Exception as e:
                        media_urls.append({
                            "provider": p2p_key,
                            "status": "error",
                            "error": str(e)
                        })

        # =================================================
        # HANDLE DTSHCODE
        # =================================================

        elif response_json.get("type") == "dtshcode":

            sub_soup = BeautifulSoup(embed_url, "html.parser")
            iframe = sub_soup.select_one("iframe")

            if iframe and iframe.get("src"):
                try:
                    sw_res = streamwish.real_extract(
                        iframe["src"],
                        request
                    )
                    media_urls.append({
                        "provider": "streamwish",
                        "result": sw_res
                    })
                except Exception as e:
                    media_urls.append({
                        "provider": "streamwish",
                        "status": "error",
                        "error": str(e)
                    })
            else:
                response_data["error"] = "Could not find iframe inside dtshcode."
                return response_data

        # =================================================
        # NO RESULTS
        # =================================================

        if not media_urls:
            response_data["error"] = {
                "message": "No playable media URLs found",
                "embed_url": embed_url,
                "response_json": response_json,
                "embed_data": (
                    embed_data
                    if 'embed_data' in locals()
                    else None
                )
            }
            return response_data

        # =================================================
        # SUCCESS
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
