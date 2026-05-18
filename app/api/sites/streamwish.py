# streamwish.py - No Django dependencies
import requests
import re
import ast
from bs4 import BeautifulSoup

TAG = 'streamwish'
multimovies_domain = 'https://multimovies.fyi'

initial_headers = {
    'Referer': multimovies_domain,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

session = requests.Session()

def to_base_36(n):
    """Converts a number to base-36"""
    if n == 0:
        return ''
    return to_base_36(n // 36) + "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36]

def real_extract(url, request):
    """Extracts streaming URLs from the given video page."""
    response_data = {
        'status': 'error',
        'status_code': 500,
        'error': None,
        'tag': TAG,
        'headers': None,
        'streaming_url': None
    }
    
    try:
        print(f"StreamWish extracting: {url}")
        
        # Add timeout to prevent hanging
        initial_response = session.get(url, headers=initial_headers, timeout=10)
        initial_response.raise_for_status()
        
        response_text = initial_response.text
        
        if "File is no longer" in response_text:
            response_data['status'] = 'failed'
            response_data['status_code'] = 200
            response_data['error'] = 'Link Expired!'
            return response_data
        
        # Parse HTML
        soup = BeautifulSoup(response_text, 'html.parser')
        
        # Find packed JavaScript
        js_code = None
        for script in soup.find_all('script'):
            if script.string and "eval(function(p,a,c,k,e,d)" in script.string:
                js_code = script.string
                break
        
        if not js_code:
            response_data['error'] = 'No packed JS found'
            return response_data
        
        # Extract and clean the JS code
        encoded_packed = re.sub(r"eval\(function\([^\)]*\)\{[^\}]*\}\(|.split\('\|'\)\)\)", '', js_code)
        
        # Safely evaluate the packed data
        try:
            data = ast.literal_eval(encoded_packed)
        except:
            response_data['error'] = 'Failed to parse packed data'
            return response_data
        
        if not isinstance(data, (list, tuple)) or len(data) < 4:
            response_data['error'] = 'Invalid packed data structure'
            return response_data
        
        # Extract values from packed data
        p = data[0]
        a = int(data[1])
        c = int(data[2])
        k = data[3].split('|')
        
        # Replace placeholders with corresponding values
        for i in range(c):
            if k[c - i - 1]:
                pattern = r'\b' + to_base_36(c - i - 1) + r'\b'
                p = re.sub(pattern, k[c - i - 1], p)
        
        # Get Video URL
        video_match = re.search(r'"hls2":"([^"]+)', p)
        if not video_match:
            video_match = re.search(r"hls2:\s*'([^']+)", p)
        
        if not video_match:
            response_data['error'] = 'Video URL not found in unpacked code'
            return response_data
        
        video_url = video_match.group(1)
        
        # Prepare response
        response_data['status'] = 'success'
        response_data['status_code'] = 200
        response_data['headers'] = initial_headers
        response_data['streaming_url'] = video_url
        
    except requests.exceptions.Timeout:
        response_data['error'] = 'Request timeout'
    except requests.exceptions.RequestException as e:
        response_data['error'] = f'Request failed: {str(e)}'
    except Exception as e:
        response_data['error'] = f'Extraction failed: {str(e)}'
        import traceback
        print(traceback.format_exc())
    
    return response_data
