import requests
from django.http import StreamingHttpResponse, JsonResponse
from urllib.parse import urlparse, urljoin, quote, unquote
import time
import m3u8
from django.contrib.sites.shortcuts import get_current_site
from base64 import b64decode, b64encode
import json 

HOP_BY_HOP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailer', 'transfer-encoding', 'upgrade'
}

# --- NEW HELPER FUNCTION ---
def get_safe_headers(encoded_headers):
    """Safely decode base64 headers into a dictionary."""
    if not encoded_headers:
        return {}
    try:
        decoded = safe_b64decode(encoded_headers)
        return json.loads(decoded) if decoded else {}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {}

def safe_b64decode(value):
    try:
        # Some players might not send proper padding, let's fix that
        padding = '=' * (4 - len(value) % 4)
        return b64decode(unquote(value) + padding).decode()
    except Exception:
        return unquote(value)

def remove_hop_by_hop_headers(response):
    for header in HOP_BY_HOP_HEADERS:
        if header in response.headers:
            del response.headers[header]
    return response

def get_domain(request):
    current_site = get_current_site(request)
    return f"{request.scheme}://{current_site.domain}"

def generate_m3u8(playlist_items, is_master=False):
    m3u8_content = "#EXTM3U\n"
    if is_master:
        m3u8_content += "#EXT-X-VERSION:3\n"
        for item in playlist_items:
            if item.get("type") == "audio":
                m3u8_content += f"#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID=\"audio\",NAME=\"Audio\",URI=\"{item['uri']}\"\n"
            else:
                m3u8_content += (
                    f"#EXT-X-STREAM-INF:BANDWIDTH={item['bandwidth']},RESOLUTION={item.get('resolution', (0, 0))[0]}x{item.get('resolution', (0, 0))[1]},AUDIO=\"audio\"\n"
                    f"{item['uri']}\n"
                )
    else:
        m3u8_content += "#EXT-X-TARGETDURATION:10\n#EXT-X-ALLOW-CACHE:YES\n#EXT-X-PLAYLIST-TYPE:VOD\n#EXT-X-VERSION:3\n#EXT-X-MEDIA-SEQUENCE:1\n"
        for item in playlist_items:
            if "#EXT-X-MAP" in item['info']:
                m3u8_content += f"{item['info']}\n"
            else:
                m3u8_content += f"{item['info']}\n{item['uri']}\n"
        m3u8_content += "#EXT-X-ENDLIST\n"
    return m3u8_content

def proxy_view(request):
    """Entry point for master and media playlists."""
    encoded_url = request.GET.get('url', '')
    encoded_headers = request.GET.get('headers', '')
    
    # SAFE DECODING
    hls_url = safe_b64decode(encoded_url)
    if not hls_url:
        return JsonResponse({"error": "URL is required"}, status=400)
    
    HEADERS = get_safe_headers(encoded_headers)
    
    # Re-encode for children (keeps headers consistent)
    safe_encoded_headers = quote(b64encode(json.dumps(HEADERS).encode()).decode())

    try:
        playlist_response = requests.get(hls_url, headers=HEADERS, timeout=10)
        playlist_response.raise_for_status()
        m3u8_playlist = m3u8.loads(playlist_response.text)
    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch playlist: {str(e)}"}, status=502)
    
    playlist_items = []
    is_master = m3u8_playlist.is_variant  

    if is_master:
        for variant in m3u8_playlist.playlists:
            uri = variant.uri
            complete_url = uri if bool(urlparse(uri).netloc) else urljoin(hls_url, uri)
            proxied_url = f"{get_domain(request)}/proxy/?headers={safe_encoded_headers}&url={quote(complete_url)}"
            playlist_items.append({
                'uri': proxied_url,
                'resolution': variant.stream_info.resolution,
                'bandwidth': variant.stream_info.bandwidth
            })
        for media in m3u8_playlist.media:
            if media.type == "AUDIO":
                complete_url = media.uri if bool(urlparse(media.uri).netloc) else urljoin(hls_url, media.uri)
                proxied_url = f"{get_domain(request)}/proxy/?headers={safe_encoded_headers}&url={quote(complete_url)}"
                playlist_items.append({'uri': proxied_url, 'type': 'audio'})
    else:
        if m3u8_playlist.segments and m3u8_playlist.segment_map:
            init_uri = m3u8_playlist.segment_map[0].uri
            complete_init = init_uri if bool(urlparse(init_uri).netloc) else urljoin(hls_url, init_uri)
            proxied_init = f"{get_domain(request)}/proxy/stream/?headers={safe_encoded_headers}&ts_url={quote(complete_init)}"
            playlist_items.append({'info': f"#EXT-X-MAP:URI=\"{proxied_init}\"", 'uri': ''})

        for segment in m3u8_playlist.segments:
            complete_url = segment.uri if bool(urlparse(segment.uri).netloc) else urljoin(hls_url, segment.uri)
            proxied_url = f"{get_domain(request)}/proxy/stream/?headers={safe_encoded_headers}&ts_url={quote(complete_url)}"
            playlist_items.append({'info': f"#EXTINF:{segment.duration},", 'uri': proxied_url})

    m3u8_content = generate_m3u8(playlist_items, is_master=is_master)
    response = StreamingHttpResponse(m3u8_content, content_type="application/vnd.apple.mpegurl")
    response['Access-Control-Allow-Origin'] = '*'
    return remove_hop_by_hop_headers(response)


def stream_ts(request):
    ts_url = request.GET.get('ts_url')
    encoded_headers = request.GET.get('headers', '')
    
    # SAFE DECODING
    HEADERS = get_safe_headers(encoded_headers)

    if not ts_url:
        return JsonResponse({"error": "Missing ts_url parameter"}, status=400)

    decoded_url = unquote(ts_url)

    # Forward Range header from client (Crucial for seeking)
    range_header = request.META.get('HTTP_RANGE')
    if range_header:
        HEADERS['Range'] = range_header

    try:
        response = requests.get(decoded_url, stream=True, headers=HEADERS, timeout=15)
        response.raise_for_status()

        # Content-Type logic
        content_type = response.headers.get('Content-Type', 'video/mp2t')
        if decoded_url.endswith('.m4s'): content_type = 'video/iso.segment'
        elif decoded_url.endswith('.mp4'): content_type = 'video/mp4'

        response_headers = {k: v for k, v in response.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}
        response_headers['Access-Control-Allow-Origin'] = '*'
        response_headers['Accept-Ranges'] = 'bytes'

        return StreamingHttpResponse(
            streaming_content=response.iter_content(chunk_size=8192),
            content_type=content_type,
            status=response.status_code,
            headers=response_headers
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
