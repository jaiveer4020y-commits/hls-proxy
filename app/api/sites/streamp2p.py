import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from urllib.parse import urlparse
from . import site_domains


TAG = 'rpmhub'

user_agent = (
    "Mozilla/5.0 (Linux; Android 10; K) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/132.0.0.0 Mobile Safari/537.36"
)


def real_extract(url, request):

    # Extract domain and video ID
    # Example:
    # https://multimovies.rpmhub.site/#965unp

    parsed = urlparse(url)

    domain = f"{parsed.scheme}://{parsed.netloc}"
    video_id = parsed.fragment

    headers = {
        "Referer": domain + "/",
        "User-Agent": user_agent
    }

    # Fetch the page first
    requests.get(
        url,
        headers=headers,
        timeout=15
    )

    # API containing encrypted video information
    api = f"{domain}/api/v1/video?id={video_id}"

    response = requests.get(
        api,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    encrypted_data = response.text.strip()

    # AES-CBC configuration
    password = "kiemtienmua911ca"
    iv_str = "1234567890oiuytr"

    key = password.encode("utf-8")
    iv = iv_str.encode("utf-8")

    # Encrypted API response is hexadecimal
    encrypted_bytes = bytes.fromhex(encrypted_data)

    # AES-CBC decrypt
    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )

    decrypted_bytes = cipher.decrypt(encrypted_bytes)

    # Remove PKCS7 padding
    decrypted_json = unpad(
        decrypted_bytes,
        AES.block_size
    ).decode("utf-8")

    # Convert decrypted JSON to Python object
    decrypted_data = json.loads(decrypted_json)

    # Print EVERYTHING decrypted
    print(
        json.dumps(
            decrypted_data,
            indent=2,
            ensure_ascii=False
        )
    )

    # Return EVERYTHING decrypted, without removing fields
    return {
        "status": "success",
        "status_code": 200,
        "tag": TAG,
        "headers": headers,
        "streaming_url": decrypted_data.get("cf"),
        "decrypted_data": decrypted_data
    }
