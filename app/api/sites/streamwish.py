import requests
from bs4 import BeautifulSoup
import re
from django.http import JsonResponse
import json
import ast
from urllib.parse import quote, unquote
from django.contrib.sites.shortcuts import get_current_site
from . import site_domains

# Configuration
TAG = 'streamwish'
default_domain = site_domains.get_domain('streamwish')
multimovies_domain = site_domains.get_domain('multimovies')

initial_headers = {
    'Referer': multimovies_domain,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

# Helper Functions
def get_domain(request):
    """Returns the base domain of the request."""
    current_site = get_current_site(request)
    return f"{request.scheme}://{current_site.domain}"

def to_base_36(n):
    """Converts a number to base-36 using an iterative approach."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    if n < 36:
        return chars[n]

    result = ""

    while n:
        n, i = divmod(n, 36)
        result = chars[i] + result

    return result

# Create session
session = requests.Session()

qualities = ['144', '240', '360', '480', '720', '1080']


def real_extract(url, request):
    """Extracts streaming URLs from the given video page."""

    response_data = {
        'status': 'error',
        'status_code': 400,
        'error': None,
        'tag': TAG,
        'headers': initial_headers,
        'streaming_url': None
    }

    try:

        # =================================================
        # Fetch page
        # =================================================

        response = session.get(
            url,
            headers=initial_headers,
            timeout=20
        )

        initial_response = response.text

        # =================================================
        # Expired file check
        # =================================================

        if "File is no longer" in initial_response:

            response_data['status'] = 'failed'
            response_data['status_code'] = 200
            response_data['error'] = 'Link Expired!'
            response_data['streaming_url'] = None

            return response_data

        # =================================================
        # Parse HTML
        # =================================================

        soup = BeautifulSoup(initial_response, 'html.parser')

        js_code = ""

        for script in soup.find_all('script'):

            if (
                script.string
                and "eval(function(p,a,c,k,e,d)" in script.string
            ):

                js_code = script.string
                break

        if not js_code:

            response_data['error'] = (
                'Packed JS not found.'
            )

            return response_data

        # =================================================
        # Extract packed JS
        # =================================================

        encoded_packed = re.sub(
            r"eval\(function\([^\)]*\)\{[^\}]*\}\(|.split\('\|'\)\)\)",
            '',
            js_code
        )

        try:
            data = ast.literal_eval(encoded_packed)

        except Exception as e:

            response_data['error'] = (
                f'Packed JS parse failed: {str(e)}'
            )

            return response_data

        # =================================================
        # Validate packed data
        # =================================================

        if len(data) < 4:

            response_data['error'] = (
                'Packed JS structure invalid.'
            )

            return response_data

        p = data[0]
        a = int(data[1])
        c = int(data[2])
        k = data[3].split('|')

        # =================================================
        # Decode packed JS
        # =================================================

        for i in range(c):

            if k[c - i - 1]:

                p = re.sub(
                    r'\b' + to_base_36(c - i - 1) + r'\b',
                    k[c - i - 1],
                    p
                )

        # =================================================
        # Extract video URL
        # =================================================

        video_patterns = [
            r'"hls2":"([^"]+)',
            r'"file":"([^"]+)',
            r'sources:\s*\[\{file:\s*"([^"]+)',
            r'https?:\/\/[^\s"\']+\.m3u8[^\s"\']*'
        ]

        video_url = None

        for pattern in video_patterns:

            match = re.search(pattern, p)

            if match:

                if match.groups():
                    video_url = match.group(1)
                else:
                    video_url = match.group(0)

                break

        # =================================================
        # Final URL validation
        # =================================================

        if not video_url:

            response_data['error'] = (
                'Could not extract streaming URL.'
            )

            return response_data

        # =================================================
        # Clean URL
        # =================================================

        video_url = (
            video_url
            .replace('\\/', '/')
            .replace('\\\\', '')
        )

        # =================================================
        # Success
        # =================================================

        response_data['status'] = 'success'
        response_data['status_code'] = 200
        response_data['headers'] = initial_headers
        response_data['streaming_url'] = video_url

        return response_data

    except requests.exceptions.Timeout:

        response_data['error'] = 'Request timed out.'

    except requests.exceptions.RequestException as e:

        response_data['error'] = (
            f'HTTP request failed: {str(e)}'
        )

    except Exception as e:

        response_data['error'] = (
            f'[STREAMWISH] Unexpected error: {str(e)}'
        )

    return response_data
