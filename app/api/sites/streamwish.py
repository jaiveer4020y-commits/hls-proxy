# streamwish.py - Django compatible version for Vercel
import requests
from bs4 import BeautifulSoup
import re
import ast
import json
from urllib.parse import quote, unquote

# Try to import Django components with fallback for serverless
try:
    from django.http import JsonResponse
    from django.contrib.sites.shortcuts import get_current_site
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    # Create dummy functions for when Django isn't available
    def JsonResponse(data, status=200):
        return {"status": status, "data": data}
    
    def get_current_site(request):
        return type('obj', (object,), {'domain': 'multimovies.fyi'})

from . import site_domains

# Configuration
TAG = 'streamwish'

# Safe domain getter with fallback
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

# Global response data template
response_data = {
    'status': None,
    'status_code': None,
    'error': None,
    'tag': TAG,
    'headers': None,
    'streaming_url': None
}

# Create session
session = requests.Session()
session.headers.update(initial_headers)

# Quality options
qualities = ['144', '240', '360', '480', '720', '1080']

def get_domain(request):
    """Returns the base domain of the request with fallback"""
    if DJANGO_AVAILABLE and request:
        try:
            current_site = get_current_site(request)
            return f"{request.scheme}://{current_site.domain}"
        except:
            pass
    return multimovies_domain

def to_base_36(n):
    """Converts a number to base-36 using recursion"""
    if n == 0:
        return ''
    return to_base_36(n // 36) + "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36]

def extract_packed_js(js_code):
    """Extract video URL from packed JavaScript"""
    try:
        # Clean the packed code
        encoded_packed = re.sub(r"eval\(function\([^\)]*\)\{[^\}]*\}\(|.split\('\|'\)\)\)", '', js_code)
        
        # Parse the packed data
        data = ast.literal_eval(encoded_packed)
        
        if not isinstance(data, (list, tuple)) or len(data) < 4:
            return None
        
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
        
        # Try multiple patterns to find video URL
        patterns = [
            r'"hls2":"([^"]+)',
            r'"hls2":"(.*?)"',
            r"hls2:\s*'([^']+)'",
            r'hls2:\s*"([^"]+)"',
            r'"file":"([^"]+)"',
            r'file:\s*"([^"]+)"',
            r'src:\s*"([^"]+\.m3u8)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, p)
            if match:
                video_url = match.group(1)
                # Clean and decode URL if needed
                video_url = video_url.replace('\\/', '/')
                return video_url
        
        return None
        
    except Exception as e:
        print(f"Error extracting packed JS: {e}")
        return None

def real_extract(url, request=None):
    """Extracts streaming URLs from the given video page."""
    
    # Reset response data for each call
    result_data = response_data.copy()
    
    try:
        # Validate URL
        if not url:
            result_data['status'] = 'error'
            result_data['status_code'] = 400
            result_data['error'] = 'No URL provided'
            return result_data
        
        # Make request with timeout
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            result_data['status'] = 'error'
            result_data['status_code'] = 504
            result_data['error'] = 'Request timeout'
            return result_data
        except requests.exceptions.RequestException as e:
            result_data['status'] = 'error'
            result_data['status_code'] = 500
            result_data['error'] = f'Request failed: {str(e)}'
            return result_data
        
        response_text = response.text
        
        # Check for expired link
        if "File is no longer" in response_text:
            result_data['status'] = 'failed'
            result_data['status_code'] = 200
            result_data['error'] = 'Link Expired!'
            result_data['streaming_url'] = None
            return result_data
        
        # Parse HTML
        soup = BeautifulSoup(response_text, 'html.parser')
        
        # Find packed JavaScript
        js_code = None
        for script in soup.find_all('script'):
            if script.string and "eval(function(p,a,c,k,e,d)" in script.string:
                js_code = script.string
                break
        
        # If no packed JS found, try to find direct video URL
        if not js_code:
            # Look for video sources
            video_sources = []
            
            # Check for video tags
            for video in soup.find_all('video'):
                for source in video.find_all('source'):
                    if source.get('src'):
                        video_sources.append(source.get('src'))
            
            # Check for iframes
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src')
                if src and ('.m3u8' in src or '.mp4' in src):
                    video_sources.append(src)
            
            if video_sources:
                result_data['status'] = 'success'
                result_data['status_code'] = 200
                result_data['headers'] = initial_headers
                result_data['streaming_url'] = video_sources[0]
                return result_data
            else:
                result_data['error'] = 'No packed JS or video source found'
                return result_data
        
        # Extract video URL from packed JavaScript
        video_url = extract_packed_js(js_code)
        
        if not video_url:
            result_data['error'] = 'Could not extract video URL from packed JS'
            return result_data
        
        # Prepare success response
        result_data['status'] = 'success'
        result_data['status_code'] = 200
        result_data['headers'] = initial_headers
        result_data['streaming_url'] = video_url
        
    except Exception as e:
        result_data['status'] = 'error'
        result_data['status_code'] = 500
        result_data['error'] = f'Extraction failed: {str(e)}'
        # Add debug info
        result_data['debug'] = {
            'exception_type': type(e).__name__,
            'url': url
        }
    
    return result_data

# Helper function to get available qualities (if needed)
def get_qualities(streaming_url):
    """Get available qualities from master.m3u8"""
    try:
        response = session.get(streaming_url, timeout=10)
        if response.status_code == 200:
            # Parse m3u8 content to find available qualities
            lines = response.text.split('\n')
            available_qualities = []
            for line in lines:
                if '.m3u8' in line and 'resolution=' in line:
                    match = re.search(r'RESOLUTION=\d+x(\d+)', line)
                    if match:
                        available_qualities.append(match.group(1))
            return available_qualities if available_qualities else qualities
    except:
        pass
    return qualities
