import requests
import re
import base64
import json
import ast
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


def extract_m3u8(embed_url):
    """Fetch embed page and extract m3u8 link"""
    try:
        resp = session.get(embed_url, headers=headers, timeout=15)
        resp.raise_for_status()
        m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', resp.text)
        if m3u8_match:
            return m3u8_match.group(1)
    except Exception:
        return None
    return None


def real_extract(url, request):
    """Extracts the streaming URL from the given URL."""
    response_data = {
        'status': 'error',
        'status_code': 400,
        'error': None,
        'embed_urls': None,
        'servers': []
    }

    try:
        iframe_urls = {}
        sid = urlparse(url).path.rstrip("/").split("/")[-1]

        # Fetch streaming data
        post_response = session.get(
            f"{PROXY_API}?type=post&post_sid={sid}&url=https://pro.gtxgamer.site/embedhelper.php",
            headers=headers,
            timeout=15
        )
        post_response.raise_for_status()
        post_json = post_response.json()

        if 'mresult' not in post_json:
            response_data['error'] = 'Invalid response structure'
            return response_data

        # Decode safely
        decoded_data = base64.b64decode(post_json['mresult']).decode("utf-8").strip()

        try:
            json_data = json.loads(decoded_data)
        except json.JSONDecodeError:
            # fallback if the payload isn't strict JSON
            json_data = ast.literal_eval(decoded_data)

        # Build servers list
        servers = []

        if 'smwh' in json_data:
            embed_url = f"{streamwish_domain}/e/{json_data['smwh']}"
            iframe_urls['streamwish'] = embed_url
            m3u8 = extract_m3u8(embed_url)
            if m3u8:
                servers.append({"server": "streamwish", "m3u8": m3u8})

        if 'strmp2' in json_data:
            embed_url = f"{streamp2p_domain}/#{json_data['strmp2']}"
            iframe_urls['streamp2p'] = embed_url
            m3u8 = extract_m3u8(embed_url)
            if m3u8:
                servers.append({"server": "streamp2p", "m3u8": m3u8})

        # Success
        response_data['status'] = 'success'
        response_data['status_code'] = 200
        response_data['error'] = None
        response_data['embed_urls'] = iframe_urls
        response_data['servers'] = servers

    except requests.exceptions.RequestException as e:
        response_data['error'] = f'HTTP request failed: {str(e)}'
    except (json.JSONDecodeError, ValueError, SyntaxError):
        response_data['error'] = 'Failed to parse decoded response'
    except base64.binascii.Error:
        response_data['error'] = 'Failed to decode base64 response'
    except Exception as e:
        response_data['error'] = f'[GDMirror] Unexpected error: {str(e)}'

    return response_data
