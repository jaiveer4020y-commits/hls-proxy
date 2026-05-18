# streamwish.py - Keep your original Django imports
import requests
from bs4 import BeautifulSoup
import re
import ast
from urllib.parse import quote, unquote

# Fix Django imports - add try-except for Vercel
try:
    from django.http import JsonResponse
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    # Dummy fallbacks for Vercel
    JsonResponse = None
    def get_current_site(request):
        return type('obj', (object,), {'domain': 'multimovies.fyi'})

from . import site_domains

# Configuration
TAG = 'streamwish'

# FIX: Add try-except for domain lookup
try:
    default_domain = site_domains.get_domain('streamwish')
except:
    default_domain = 'https://streamwish.com'

try:
    multimovies_domain = site_domains.get_domain('multimovies')
except:
    multimovies_domain = 'https://multimovies.fyi'

initial_headers = {
    'Referer': multimovies_domain,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

# Helper Functions
def get_domain(request):
    """Returns the base domain of the request."""
    try:
        current_site = get_current_site(request)
        return f"{request.scheme}://{current_site.domain}"
    except:
        return multimovies_domain

def to_base_36(n):
    """Converts a number to base-36"""
    if n == 0:
        return ''
    return to_base_36(n // 36) + "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36]

# Global response data (FIX: Create new dict each call to avoid mutation)
def get_response_template():
    return {
        'status': None,
        'status_code': None,
        'error': None,
        'tag': TAG,
        'headers': None,
        'streaming_url': None
    }

# Create session
session = requests.Session()

qualities = ['144', '240', '360', '480', '720', '1080']

def real_extract(url, request):
    """Extracts streaming URLs from the given video page."""
    
    # FIX: Create fresh response data for each call
    response_data = get_response_template()
    
    try:
        # Validate URL
        if not url:
            response_data['status'] = 'error'
            response_data['status_code'] = 400
            response_data['error'] = 'No URL provided'
            return response_data
        
        # FIX: Add timeout and error handling
        try:
            initial_response = session.get(url, headers=initial_headers, timeout=15)
            initial_response.raise_for_status()
            response_text = initial_response.text
        except requests.exceptions.Timeout:
            response_data['status'] = 'error'
            response_data['status_code'] = 504
            response_data['error'] = 'Request timeout'
            return response_data
        except requests.exceptions.RequestException as e:
            response_data['status'] = 'error'
            response_data['status_code'] = 500
            response_data['error'] = f'Request failed: {str(e)}'
            return response_data
        
        # Check for expired link
        if "File is no longer" in response_text:
            response_data['status'] = 'failed'
            response_data['status_code'] = 200
            response_data['error'] = 'Link Expired!'
            response_data['streaming_url'] = None
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
        
        # FIX: Safely evaluate with try-except
        try:
            data = ast.literal_eval(encoded_packed)
        except Exception as e:
            response_data['error'] = f'Failed to parse packed data: {str(e)}'
            return response_data
        
        # Validate data structure
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
        
        # Get Video URL - FIX: Add multiple patterns
        video_url = None
        patterns = [
            r'"hls2":"([^"]+)',
            r'"hls2":"(.*?)"',
            r"hls2:\s*'([^']+)'",
            r'"file":"([^"]+\.m3u8)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, p)
            if match:
                video_url = match.group(1)
                break
        
        if not video_url:
            response_data['error'] = 'Video URL not found in unpacked code'
            return response_data
        
        # Prepare response
        response_data['status'] = 'success'
        response_data['status_code'] = 200
        response_data['headers'] = initial_headers
        response_data['streaming_url'] = video_url
        
    except Exception as e:
        response_data['status'] = 'error'
        response_data['status_code'] = 500
        response_data['error'] = f'Extraction failed: {str(e)}'
        # Don't crash - return error gracefully
    
    return response_data
