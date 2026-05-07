import requests
from bs4 import BeautifulSoup
from . import streamwish, gdmirrorbot, streamp2p, site_domains
from . import utils as u

# Updated headers to look more like a legitimate browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest'
}

session = requests.Session()

def real_extract(url, request):
    response_data = {
        'status': 'error',
        'status_code': 400,
        'error': None,
        'servers': []
    }

    if not url:
        response_data['error'] = "No URL provided to extractor."
        return response_data

    try:
        # 1. Resolve Domain and Initial Connection
        domain = u.get_domain(url)
        try:
            init_res = session.get(domain, headers=headers, timeout=10, allow_redirects=True)
            default_domain = u.get_domain(init_res.url)
        except Exception as e:
            response_data['error'] = f"Could not resolve base domain: {str(e)}"
            return response_data

        # 2. Fetch the Video Page
        target_url = url.replace(domain, default_domain)
        response = session.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()

        # 3. Parse HTML and find Player
        soup = BeautifulSoup(response.text, 'html.parser')
        player_element = soup.select_one("#player-option-1")

        if not player_element:
            response_data['error'] = "Player element (#player-option-1) not found on page. The site layout might have changed."
            return response_data

        # 4. Extract POST attributes
        post_id = player_element.get('data-post')
        data_type = player_element.get('data-type')
        data_nume = player_element.get('data-nume')

        if not all([post_id, data_type, data_nume]):
            response_data['error'] = f"Missing data attributes: post={post_id}, type={data_type}, nume={data_nume}"
            return response_data

        # 5. Execute AJAX POST Request
        ajax_url = f"{default_domain.rstrip('/')}/wp-admin/admin-ajax.php"
        payload = {
            'action': 'doo_player_ajax',
            'post': post_id,
            'nume': data_nume,
            'type': data_type
        }
        
        post_headers = headers.copy()
        post_headers['Referer'] = target_url
        
        post_res = session.post(ajax_url, data=payload, headers=post_headers, timeout=15)
        
        # --- CRITICAL ERROR DETECTION: Check if response is actually JSON ---
        if "application/json" not in post_res.headers.get("Content-Type", ""):
            response_data['error'] = f"Site blocked request (WAF). Expected JSON but got {post_res.headers.get('Content-Type')}. Preview: {post_res.text[:100]}"
            return response_data

        try:
            response_json = post_res.json()
        except ValueError:
            response_data['error'] = "The server returned a response that isn't valid JSON."
            return response_data

        if not response_json or 'embed_url' not in response_json:
            response_data['error'] = "AJAX success, but 'embed_url' is missing from the data."
            return response_data

        embed_url = response_json['embed_url']
        media_urls = []

        # 6. Handle Content Types
        if response_json.get('type') == 'iframe':
            embed_data = gdmirrorbot.real_extract(embed_url, request)
            
            if not u.isDict(embed_data) or embed_data.get('status') == 'error':
                response_data['error'] = f"Sub-extractor (gdmirrorbot) failed: {embed_data.get('error', 'Unknown Error')}"
                return response_data

            embed_urls = embed_data.get('embed_urls', {})
            
            # Extract specific sources
            sw_url = embed_urls.get('streamwish')
            if sw_url:
                sw_res = streamwish.real_extract(sw_url, request)
                if sw_res.get('status') == 'success': media_urls.append(sw_res)
            
            sp2p_url = embed_urls.get('streamp2p')
            if sp2p_url:
                sp2p_res = streamp2p.real_extract(sp2p_url, request)
                if sp2p_res.get('status') == 'success': media_urls.append(sp2p_res)

        elif response_json.get('type') == 'dtshcode':
            sub_soup = BeautifulSoup(embed_url, 'html.parser')
            iframe = sub_soup.select_one('iframe')
            if iframe and iframe.get('src'):
                sw_res = streamwish.real_extract(iframe['src'], request)
                if sw_res.get('status') == 'success': media_urls.append(sw_res)
            else:
                response_data['error'] = "Could not find iframe inside dtshcode."
                return response_data

        # 7. Final Verification
                # 7. Final Verification & Detailed Debugging
        if not media_urls:
            # Check if gdmirrorbot even gave us URLs to begin with
            if 'embed_urls' not in locals() or not embed_urls:
                response_data['error'] = "Extraction failed: gdmirrorbot (the middleman) returned no server links."
            else:
                # Tell us exactly which servers were attempted and failed
                attempted = list(embed_urls.keys())
                response_data['error'] = f"Found servers {attempted}, but ALL failed to extract. Site is likely blocking Vercel."
            
            return response_data
