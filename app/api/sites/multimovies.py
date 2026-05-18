import requests
from bs4 import BeautifulSoup
import traceback
import sys

# =========================================================
# IMPORTS - Comment out any that don't exist yet
# =========================================================

try:
    from . import streamwish
except ImportError:
    streamwish = None
    print("Warning: streamwish module not found")

try:
    from . import gdmirrorbot
except ImportError:
    gdmirrorbot = None
    print("Warning: gdmirrorbot module not found")

try:
    from . import streamp2p
except ImportError:
    streamp2p = None
    print("Warning: streamp2p module not found")

try:
    from . import utils as u
except ImportError:
    u = None
    print("Warning: utils module not found")

# =========================================================
# HEADERS
# =========================================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Cache-Control": "max-age=0",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

# Page fetch proxy (GET)
FETCH_PROXY = "https://script.google.com/macros/s/AKfycbzwlgaq7IkI4NkLokhTcL7zxf-aiD9GZB0S4grtOuNofuw-Yzr3pmKX_6uhit4IQx8Y/exec"

# AJAX POST proxy (POST)
AJAX_PROXY = "https://script.google.com/macros/s/AKfycbxYpDKI--p7xkeOC4NT2R8rN26N6H5H6_EuQwkrAjNIliRcxf55ByXOs1RGHUK-l5PuFw/exec"

# =========================================================
# SESSION
# =========================================================

session = requests.Session()

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_domain(url):
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url.split('/')[0] + '//' + url.split('/')[2]

# =========================================================
# MAIN EXTRACTOR
# =========================================================

def real_extract(url, request):
    """
    Main extractor function for Vercel serverless
    """
    
    response_data = {
        "status": "error",
        "status_code": 500,
        "error": None,
        "servers": [],
        "debug": []
    }
    
    # Global try-catch to prevent crashes
    try:
        
        # Validate URL
        if not url:
            response_data["error"] = "No URL provided to extractor."
            response_data["status_code"] = 400
            return response_data
        
        response_data["debug"].append({
            "step": "initialization",
            "status": "success",
            "url": url,
            "python_version": sys.version,
            "modules": {
                "streamwish": streamwish is not None,
                "gdmirrorbot": gdmirrorbot is not None,
                "streamp2p": streamp2p is not None,
                "utils": u is not None
            }
        })
        
        # =================================================
        # Resolve domain
        # =================================================
        
        try:
            if u and hasattr(u, 'get_domain'):
                domain = u.get_domain(url)
            else:
                domain = get_domain(url)
            
            default_domain = domain
            
            response_data["debug"].append({
                "step": "resolve_domain",
                "status": "success",
                "default_domain": default_domain
            })
            
        except Exception as e:
            response_data["error"] = f"Could not resolve base domain: {str(e)}"
            response_data["status_code"] = 500
            return response_data
        
        # =================================================
        # Fetch page via Google fetch proxy
        # =================================================
        
        target_url = url.replace(domain, default_domain) if domain else url
        
        try:
            response = session.get(
                FETCH_PROXY,
                params={"type": "fetch", "url": target_url},
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            
            response_data["debug"].append({
                "step": "fetch_page",
                "status": "success",
                "target_url": target_url,
                "response_length": len(response.text)
            })
            
        except requests.exceptions.Timeout:
            response_data["error"] = "Fetch page timeout"
            response_data["status_code"] = 504
            return response_data
        except Exception as e:
            response_data["error"] = f"Failed to fetch page: {str(e)}"
            response_data["status_code"] = 500
            return response_data
        
        # =================================================
        # Parse HTML
        # =================================================
        
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            
            player_element = soup.select_one("#player-option-1")
            
            # fallback selector
            if not player_element:
                player_element = soup.select_one("[data-post]")
            
            if not player_element:
                response_data["error"] = "Player element not found on page."
                response_data["status_code"] = 404
                return response_data
            
            response_data["debug"].append({
                "step": "find_player",
                "status": "success"
            })
            
        except Exception as e:
            response_data["error"] = f"Failed to parse HTML: {str(e)}"
            return response_data
        
        # =================================================
        # Extract player data
        # =================================================
        
        try:
            post_id = player_element.get("data-post")
            data_type = player_element.get("data-type")
            data_nume = player_element.get("data-nume")
            
            if not all([post_id, data_type, data_nume]):
                response_data["error"] = f"Missing data attributes: post={post_id}, type={data_type}, nume={data_nume}"
                return response_data
            
            response_data["debug"].append({
                "step": "extract_attributes",
                "status": "success",
                "post": post_id,
                "type": data_type,
                "nume": data_nume
            })
            
        except Exception as e:
            response_data["error"] = f"Failed to extract attributes: {str(e)}"
            return response_data
        
        # =================================================
        # AJAX POST via Google AJAX proxy
        # =================================================
        
        try:
            ajax_url = f"{default_domain.rstrip('/')}/wp-admin/admin-ajax.php"
            
            post_res = session.post(
                AJAX_PROXY,
                data={
                    "url": ajax_url,
                    "action": "doo_player_ajax",
                    "post": post_id,
                    "nume": data_nume,
                    "type": data_type
                },
                headers=headers,
                timeout=15
            )
            
            content_type = post_res.headers.get("Content-Type", "")
            
            if "application/json" not in content_type:
                response_data["error"] = f"Site blocked request. Expected JSON but got {content_type}"
                return response_data
            
            try:
                response_json = post_res.json()
            except Exception:
                response_data["error"] = "Server returned invalid JSON"
                return response_data
            
            if not response_json:
                response_data["error"] = "Empty JSON response"
                return response_data
            
            response_data["debug"].append({
                "step": "ajax_response",
                "status": "success",
                "response_json": response_json
            })
            
        except Exception as e:
            response_data["error"] = f"AJAX request failed: {str(e)}"
            return response_data
        
        # =================================================
        # Get embed URL
        # =================================================
        
        embed_url = response_json.get("embed_url")
        
        if not embed_url:
            response_data["error"] = "embed_url missing in AJAX response"
            return response_data
        
        response_data["debug"].append({
            "step": "embed_url",
            "status": "success",
            "embed_url": embed_url
        })
        
        media_urls = []
        
        # =================================================
        # HANDLE IFRAME
        # =================================================
        
        if response_json.get("type") == "iframe":
            
            if not gdmirrorbot or not hasattr(gdmirrorbot, 'real_extract'):
                response_data["error"] = "gdmirrorbot module not available"
                return response_data
            
            try:
                embed_data = gdmirrorbot.real_extract(embed_url, request)
                
                response_data["debug"].append({
                    "step": "gdmirrorbot",
                    "result": embed_data
                })
                
                if not isinstance(embed_data, dict):
                    response_data["error"] = "gdmirrorbot returned invalid response"
                    return response_data
                
                if embed_data.get("status") == "error":
                    response_data["error"] = embed_data.get("error") or "gdmirrorbot extractor failed"
                    return response_data
                
                embed_urls = embed_data.get("embed_urls", {})
                
                response_data["debug"].append({
                    "step": "embed_urls",
                    "embed_urls": embed_urls
                })
                
            except Exception as e:
                response_data["error"] = f"gdmirrorbot crashed: {str(e)}\n{traceback.format_exc()}"
                return response_data
            
            # =============================================
            # Loop providers
            # =============================================
            
            for key, value in embed_urls.items():
                
                if not value:
                    continue
                
                lower_key = key.lower()
                
                try:
                    
                    # =====================================
                    # STREAMWISH / FILELIONS
                    # =====================================
                    
                    # In your main extractor's provider loop, change this section:

# =====================================
# STREAMWISH / FILELIONS / STREAMHG
# =====================================

if any(x in lower_key for x in ["streamwish", "sw", "wish", "filelions", "lion", "dwish", "streamhg", "hg"]):
    
    if not streamwish or not hasattr(streamwish, 'real_extract'):
        media_urls.append({
            "provider": key,
            "status": "error",
            "error": "StreamWish module not available"
        })
    else:
        try:
            # Use streamwish extractor for StreamHG too
            sw_res = streamwish.real_extract(value, request)
            media_urls.append({
                "provider": key,
                "result": sw_res
            })
        except Exception as e:
            media_urls.append({
                "provider": key,
                "status": "error",
                "error": f"StreamWish crashed for {key}: {str(e)}"
            })
                    
                    # =====================================
                    # STREAMP2P
                    # =====================================
                    
                    elif "p2p" in lower_key:
                        
                        if not streamp2p or not hasattr(streamp2p, 'real_extract'):
                            media_urls.append({
                                "provider": key,
                                "status": "error",
                                "error": "StreamP2P module not available"
                            })
                        else:
                            try:
                                sp2p_res = streamp2p.real_extract(value, request)
                                media_urls.append({
                                    "provider": key,
                                    "result": sp2p_res
                                })
                            except Exception as e:
                                media_urls.append({
                                    "provider": key,
                                    "status": "error",
                                    "error": f"StreamP2P crashed: {str(e)}\n{traceback.format_exc()}"
                                })
                    
                    # =====================================
                    # UNKNOWN PROVIDERS
                    # =====================================
                    
                    else:
                        media_urls.append({
                            "provider": key,
                            "status": "error",
                            "error": f"No extractor available for provider: {key}"
                        })
                        
                except Exception as e:
                    media_urls.append({
                        "provider": key,
                        "status": "error",
                        "error": f"Unexpected error in provider loop: {str(e)}"
                    })
        
        # =================================================
        # HANDLE DTSHCODE
        # =================================================
        
        elif response_json.get("type") == "dtshcode":
            
            try:
                sub_soup = BeautifulSoup(embed_url, "html.parser")
                iframe = sub_soup.select_one("iframe")
                
                if iframe and iframe.get("src"):
                    iframe_src = iframe["src"]
                    
                    if streamwish and hasattr(streamwish, 'real_extract'):
                        sw_res = streamwish.real_extract(iframe_src, request)
                        media_urls.append({
                            "provider": "streamwish",
                            "result": sw_res
                        })
                    else:
                        response_data["error"] = "StreamWish module not available for dtshcode"
                        return response_data
                else:
                    response_data["error"] = "Could not find iframe inside dtshcode"
                    return response_data
                    
            except Exception as e:
                response_data["error"] = f"Failed to process dtshcode: {str(e)}"
                return response_data
        
        # =================================================
        # NO RESULTS
        # =================================================
        
        if not media_urls:
            response_data["error"] = {
                "message": "No playable media URLs found",
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
            "servers": media_urls
        })
        
        return response_data
        
    # =====================================================
    # CATCH ALL EXCEPTIONS - PREVENT CRASH
    # =====================================================
    
    except Exception as e:
        response_data["error"] = {
            "message": f"Unhandled exception: {str(e)}",
            "traceback": traceback.format_exc(),
            "type": str(type(e).__name__)
        }
        response_data["status_code"] = 500
        return response_data
