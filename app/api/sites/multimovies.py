import cloudscraper
from bs4 import BeautifulSoup

from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u


# =========================================================
# Browser-like headers
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
# Cloudflare bypass session
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
        response_data["error"] = "No URL provided."
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
            response_data["error"] = f"Could not resolve domain: {str(e)}"
            return response_data

        # =================================================
        # Fetch target page
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
        # Parse page
        # =================================================

        soup = BeautifulSoup(response.text, "html.parser")

        player_element = soup.select_one("#player-option-1")

        if not player_element:

            # fallback selector
            player_element = soup.select_one("[data-post]")

        if not player_element:
            response_data["error"] = (
                "Player element not found. "
                "Site layout may have changed."
            )
            return response_data

        # =================================================
        # Extract attributes
        # =================================================

        post_id = player_element.get("data-post")
        data_type = player_element.get("data-type")
        data_nume = player_element.get("data-nume")

        if not all([post_id, data_type, data_nume]):

            response_data["error"] = {
                "message": "Missing player attributes",
                "post": post_id,
                "type": data_type,
                "nume": data_nume
            }

            return response_data

        # =================================================
        # AJAX Request
        # =================================================

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
        # Validate JSON response
        # =================================================

        content_type = post_res.headers.get("Content-Type", "")

        if "application/json" not in content_type:

            response_data["error"] = {
                "message": "Expected JSON but got different content type",
                "content_type": content_type,
                "preview": post_res.text[:500]
            }

            return response_data

        try:
            response_json = post_res.json()

        except Exception:

            response_data["error"] = {
                "message": "Invalid JSON response",
                "preview": post_res.text[:500]
            }

            return response_data

        # =================================================
        # Check embed URL
        # =================================================

        embed_url = response_json.get("embed_url")

        if not embed_url:

            response_data["error"] = {
                "message": "embed_url missing",
                "response_json": response_json
            }

            return response_data

        media_urls = []

        # =================================================
        # IFRAME TYPE
        # =================================================

        if response_json.get("type") == "iframe":

            print("\n========== IFRAME MODE ==========")
            print("Embed URL:", embed_url)

            embed_data = gdmirrorbot.real_extract(embed_url, request)

            print("\n========== GDMIRRORBOT ==========")
            print(embed_data)

            if not isinstance(embed_data, dict):

                response_data["error"] = (
                    "gdmirrorbot returned invalid data"
                )

                return response_data

            if embed_data.get("status") == "error":

                response_data["error"] = {
                    "message": "gdmirrorbot failed",
                    "details": embed_data
                }

                return response_data

            embed_urls = embed_data.get("embed_urls", {})

            print("\n========== EMBED URLS ==========")
            print(embed_urls)

            # =============================================
            # Auto-detect providers
            # =============================================

            for key, value in embed_urls.items():

                if not value:
                    continue

                print(f"\nTrying provider: {key}")
                print("URL:", value)

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

                        print("\nSTREAMWISH RESULT:")
                        print(sw_res)

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

                        print("\nSTREAMP2P RESULT:")
                        print(sp2p_res)

                        if (
                            isinstance(sp2p_res, dict)
                            and sp2p_res.get("status") == "success"
                        ):
                            media_urls.append(sp2p_res)

                except Exception as provider_error:

                    print(
                        f"Provider extraction failed: "
                        f"{str(provider_error)}"
                    )

        # =================================================
        # DTSHCODE TYPE
        # =================================================

        elif response_json.get("type") == "dtshcode":

            print("\n========== DTSHCODE MODE ==========")

            sub_soup = BeautifulSoup(embed_url, "html.parser")

            iframe = sub_soup.select_one("iframe")

            if iframe and iframe.get("src"):

                iframe_src = iframe["src"]

                print("Iframe SRC:", iframe_src)

                sw_res = streamwish.real_extract(
                    iframe_src,
                    request
                )

                print("\nSTREAMWISH RESULT:")
                print(sw_res)

                if (
                    isinstance(sw_res, dict)
                    and sw_res.get("status") == "success"
                ):
                    media_urls.append(sw_res)

            else:

                response_data["error"] = (
                    "Iframe not found inside dtshcode."
                )

                return response_data

        # =================================================
        # FINAL CHECK
        # =================================================

        print("\n========== FINAL MEDIA URLS ==========")
        print(media_urls)

        if not media_urls:

            response_data["error"] = {
                "message": "Extraction finished but no playable media URLs were found.",
                "embed_url": embed_url,
                "response_json": response_json
            }

            return response_data

        # =================================================
        # SUCCESS
        # =================================================

        response_data.update({
            "status": "success",
            "status_code": 200,
            "error": None,
            "servers": u.proxify(media_urls, request)
        })

        return response_data

    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        response_data["error"] = (
            "Request timed out."
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
