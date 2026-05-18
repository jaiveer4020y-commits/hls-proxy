import requests
from bs4 import BeautifulSoup
import re
import ast
from . import site_domains

TAG = 'streamwish'
multimovies_domain = site_domains.get_domain('multimovies')

initial_headers = {
    'Referer': multimovies_domain,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

session = requests.Session()

def to_base_36(n):
    return '' if n == 0 else to_base_36(n // 36) + "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36]

def real_extract(url, request):
    # Defined inside to prevent state leaking between requests
    response_data = {
        'status': None,
        'status_code': None,
        'error': None,
        'tag': TAG,
        'headers': None,
        'streaming_url': None
    }

    try:
        initial_response = session.get(url, headers=initial_headers).text

        if "File is no longer" in initial_response:
            response_data['status'] = 'failed'
            response_data['status_code'] = 200
            response_data['error'] = 'Link Expired!'
            return response_data

        soup = BeautifulSoup(initial_response, 'html.parser')

        js_code = next((
            script.string for script in soup.find_all('script')
            if script.string and "eval(function(p,a,c,k,e,d)" in script.string
        ), "")

        if js_code:
            encoded_packed = re.sub(
                r"eval\(function\([^\)]*\)\{[^\}]*\}\(|.split\('\|'\)\)\)", '', js_code
            )
            data = ast.literal_eval(encoded_packed)
            p, a, c, k = data[0], int(data[1]), int(data[2]), data[3].split('|')

            for i in range(c):
                if k[c - i - 1]:
                    p = re.sub(r'\b' + to_base_36(c - i - 1) + r'\b', k[c - i - 1], p)

            match = (
                re.search(r'"hls2":"([^"]+)', p)
                or re.search(r'file:"([^"]+\.m3u8[^"]*)"', p)
            )
            if match:
                response_data['status'] = 'success'
                response_data['status_code'] = 200
                response_data['headers'] = initial_headers
                response_data['streaming_url'] = match.group(1)
                return response_data

        # Fallback: scan raw HTML for any m3u8 URL
        match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', initial_response)
        if match:
            response_data['status'] = 'success'
            response_data['status_code'] = 200
            response_data['headers'] = initial_headers
            response_data['streaming_url'] = match.group(1)
            return response_data

        response_data['status'] = 'error'
        response_data['status_code'] = 404
        response_data['error'] = 'Could not extract streaming URL.'

    except Exception as e:
        response_data['status'] = 'error'
        response_data['status_code'] = 500
        response_data['error'] = str(e)

    return response_data
