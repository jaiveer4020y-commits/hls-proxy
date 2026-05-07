import requests
import cloudscraper
from bs4 import BeautifulSoup

from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u


# =========================================================
# HEADERS
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
    "Connection": "keep-alive"
}


# =========================================================
# SESSION
# =========================================================

session = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False
    }
)


# =========================================================
# MAIN EXTRACTOR
# =========================================================

def real_extract(url, request):

    response_data = {
        "status": "error",
        "status_code": 400,
        "error": None,
        "servers": []
    }

    if not url:
        response_data["error"] = "No URL provided to extractor."
        return response_data

    try:

        # =================================================
        # Resolve domain
        # =================================================

        domain = u.get_domain(url)

        try:
            init_res = session.get(
                domain,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )

            default_domain = u.get_domain(init_res.url)

        except Exception as e:

            response_data["error"] = (
                f"Could not resolve base domain: {str(e)}"
            )

            return response_data

        # =================================================
        # Fetch page
        # =================================================

        target_url = url.replace(domain, default_domain)

        page_headers = headers.copy()

        page_headers.update({
            "Referer": default_domain,
            "Origin": default_domain
        })

        response = session.get(
            target_url,
            headers=page_headers,
            timeout=20
        )

        response.raise_for_status()

        # =================================================
        # Parse HTML
        # =================================================

        soup = BeautifulSoup(response.text, "html.parser")

        player_element = soup.select_one("#player-option-1")

        if not player_element:
            player_element = soup.select_one("[data-post]")

        if not player_element:

            response_data["error"] = (
                "Player element not found on page."
            )

            return response_data

        # =================================================
        # Extract data attributes
        # =================================================

        post_id = player_element.get("data-post")
        data_type = player_element.get("data-type")
        data_nume = player_element.get("data-nume")

        if not all([post_id, data_type, data_nume]):

            response_data["error"] = (
                f"Missing data attributes: "
                f"post={post_id}, "
                f"type={data_type}, "
                f"nume={data_nume}"
            )

            return response_data

        # =================================================
        # AJAX POST
        # =================================================

        ajax_url = (
            f"{default_domain.rstrip('/')}"
            f"/wp-admin/admin-ajax.php"
        )

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
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        })

        post_res = session.post(
            ajax_url,
            data=payload,
            headers=post_headers,
            timeout=20
        )

        # =================================================
        # Validate response
        # =================================================

        content_type = post_res.headers.get(
            "Content-Type",
            ""
        )

        if "application/json" not in content_type:

            response_data["error"] = (
                "Site blocked request. "
                f"Expected JSON but got {content_type}. "
                f"Preview: {post_res.text[:150]}"
            )

            return response_data

        try:
            response_json = post_res.json()

        except Exception:

            response_data["error"] = (
                "Server returned invalid JSON."
            )

            return response_data

        if not response_json:

            response_data["error"] = (
                "Empty JSON response."
            )

            return response_data

        embed_url = response_json.get("embed_url")

        if not embed_url:

            response_data["error"] = (
                "embed_url missing in AJAX response."
            )

            return response_data

        media_urls = []

        # =================================================
        # HANDLE IFRAME TYPE
        # =================================================

        if response_json.get("type") == "iframe":

            embed_data = gdmirrorbot.real_extract(
                embed_url,
                request
            )

            if (
                not isinstance(embed_data, dict)
                or embed_data.get("status") == "error"
            ):

                response_data["error"] = (
                    "gdmirrorbot extractor failed."
                )

                return response_data

            embed_urls = embed_data.get(
                "embed_urls",
                {}
            )

            # =============================================
            # Auto detect providers
            # =============================================

            for key, value in embed_urls.items():

                if not value:
                    continue

                try:

                    # =====================================
                    # Streamwish / Filelions / Dwish
                    # =====================================

                    if any(
                        x in key.lower()
                        for x in [
                            "streamwish",
                            "sw",
                            "wish",
                            "filelions",
                            "lion",
                            "dwish"
                        ]
                    ):

                        sw_res = streamwish.real_extract(
                            value,
                            request
                        )

                        if (
                            isinstance(sw_res, dict)
                            and sw_res.get("status") == "success"
                        ):
                            media_urls.append(sw_res)

                    # =====================================
                    # StreamP2P
                    # =====================================

                    elif "p2p" in key.lower():

                        sp2p_res = streamp2p.real_extract(
                            value,
                            request
                        )

                        if (
                            isinstance(sp2p_res, dict)
                            and sp2p_res.get("status") == "success"
                        ):
                            media_urls.append(sp2p_res)

                except Exception:
                    pass

        # =================================================
        # HANDLE DTSHCODE
        # =================================================

        elif response_json.get("type") == "dtshcode":

            sub_soup = BeautifulSoup(
                embed_url,
                "html.parser"
            )

            iframe = sub_soup.select_one("iframe")

            if iframe and iframe.get("src"):

                iframe_src = iframe["src"]

                sw_res = streamwish.real_extract(
                    iframe_src,
                    request
                )

                if (
                    isinstance(sw_res, dict)
                    and sw_res.get("status") == "success"
                ):
                    media_urls.append(sw_res)

            else:

                response_data["error"] = (
                    "Could not find iframe inside dtshcode."
                )

                return response_data

        # =================================================
        # FINAL CHECK
        # =================================================

        if not media_urls:

            response_data["error"] = (
                "Extraction finished but no playable "
                "media URLs were found."
            )

            return response_data

        # =================================================
        # SUCCESS
        # =================================================

        response_data.update({
            "status": "success",
            "status_code": 200,
            "error": None,
            "servers": u.proxify(
                media_urls,
                request
            )
        })

    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        response_data["error"] = (
            "The request timed out."
        )

    # =====================================================
    # REQUEST ERROR
    # =====================================================

    except requests.exceptions.RequestException as e:

        response_data["error"] = (
            f"Network Error: {str(e)}"
        )

    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        response_data["error"] = (
            f"Unexpected Error: {str(e)}"
        )

    return response_data
