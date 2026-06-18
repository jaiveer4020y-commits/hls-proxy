import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from urllib.parse import urlparse
from . import site_domains


# Configuration
TAG = 'rpmhub'
user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36"

response_data = {
    'status': None,
    'status_code': None,
    'error': None,
    'tag': TAG,
    'headers': None,
    'streaming_url': None
}

def real_extract(url, request):

    # Extract domain and video_id from URL
    # URL format: https://multimovies.rpmhub.site/#965unp
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    video_id = parsed.fragment  # part after #

    headers = {
        'Referer': domain + "/",
        'User-Agent': user_agent
    }

    # Fetch page
    requests.get(url, headers=headers)

    # Get encrypted video info from API
    api = f'{domain}/api/v1/video?id={video_id}'
    encrypted_data = requests.get(api, headers=headers).text

    # Decrypt Data using AES-CBC
    password = "kiemtienmua911ca"
    iv_str  = "1234567890oiuytr"

    key = password.encode('utf-8')
    iv  = iv_str.encode('utf-8')

    # Convert hex to bytes
    encrypted_bytes = bytes.fromhex(encrypted_data)

    # Decrypt using AES CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)

    # Remove padding (PKCS7)
    decrypted_json = unpad(decrypted_bytes, AES.block_size).decode('utf-8')
    decrypted_data = json.loads(decrypted_json)
    decrypted_data = json.loads(decrypted_json)
    print(json.dumps(decrypted_data, indent=2))

    # Extract video URL
    video_url = decrypted_data.get('cf')

response_data['status'] = 'success'
response_data['status_code'] = 200
response_data['headers'] = headers
response_data['m3u8_url'] = video_url
response_data['subtitles'] = decrypted_data.get('subtitle', {})

return response_data
