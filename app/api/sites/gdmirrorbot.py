import requests
import re
import base64
import json
from urllib.parse import urlparse
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
    "Referer": default_domain,
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
}

# Create session
session = requests.Session()

PROXY_API = "https://script.google.com/macros/s/AKfycbz54yydg-bHZPUB9URu9WxcAQmtD25IV5bREsfGf-6MX4sjqlOn4sPCzeVSgLTaKMtc3Q/exec"

def real_extract(url, request):
    """Extracts the streaming URL from the given URL."""

    response_data = {
        'status': 'error',
        'status_code': 400,
        'error': None,
        'embed_urls': {},
        'debug_json_data': None,
        'debug_iframe_urls': None
    }

    try:

        iframe_urls = {}

        # =================================================
        # Extract SID
        # =================================================

        sid = urlparse(url).path.rstrip("/").split("/")[-1]

        # =================================================
        # Fetch streaming data
        # =================================================

        api_url = (
            f"{PROXY_API}"
            f"?type=post"
            f"&post_sid={sid}"
            f"&url=https://pro.iqsmartgames.com/embedhelper.php"
        )

        post_response = session.get(
            api_url,
            headers=headers,
            timeout=20
        )

        post_response.raise_for_status()

        # =================================================
        # Parse API JSON
        # =================================================

        post_json = post_response.json()

        if 'mresult' not in post_json:

            response_data['error'] = (
                'Invalid response structure: mresult missing'
            )

            response_data['debug_json_data'] = post_json

            return response_data

        # =================================================
        # Decode base64
        # =================================================

        decoded_data = base64.b64decode(
            post_json['mresult']
        ).decode("utf-8")

        # =================================================
        # Parse decoded JSON
        # =================================================

        json_data = json.loads(decoded_data)

        response_data['debug_json_data'] = json_data

        # =================================================
        # Auto detect provider keys
        # =================================================

        for key, value in json_data.items():

            if not value:
                continue

            lower_key = key.lower()

            # =============================================
            # STREAMWISH / FILELIONS / DWISH
            # =============================================

            if any(
                x in lower_key
                for x in [
                    'smwh',
                    'streamwish',
                    'wish',
                    'filelions',
                    'lion',
                    'dwish',
                    'sw'
                ]
            ):

                iframe_urls[key] = (
                    f"{streamwish_domain}/e/{value}"
                )

            # =============================================
            # STREAMP2P
            # =============================================

            elif any(
                x in lower_key
                for x in [
                    'strmp2',
                    'p2p'
                ]
            ):

                iframe_urls[key] = (
                    f"{streamp2p_domain}/#{value}"
                )

        response_data['debug_iframe_urls'] = iframe_urls

        # =================================================
        # No providers found
        # =================================================

        if not iframe_urls:

            response_data['error'] = (
                'No supported providers found in decoded JSON'
            )

            return response_data

        # =================================================
        # Success
        # =================================================

        response_data['status'] = 'success'
        response_data['status_code'] = 200
        response_data['error'] = None
        response_data['embed_urls'] = iframe_urls

    except requests.exceptions.RequestException as e:

        response_data['error'] = (
            f'HTTP request failed: {str(e)}'
        )

    except json.JSONDecodeError:

        response_data['error'] = (
            'Failed to parse JSON response'
        )

    except base64.binascii.Error:

        response_data['error'] = (
            'Failed to decode base64 response'
        )

    except Exception as e:

        response_data['error'] = (
            f'[GDMirror] Unexpected error: {str(e)}'
        )

    return response_data
