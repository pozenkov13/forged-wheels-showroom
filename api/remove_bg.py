"""
Vercel Serverless Function — Background Removal for user-uploaded wheel photos
POST /api/remove_bg

Accepts: base64 data URL of any wheel photo (from shop, internet, etc.)
Returns: base64 PNG with background removed (transparent)

Uses fal.ai BiRefNet which handles complex edges (spokes, chrome reflections).
"""

import os
import json
import base64
import time
import requests
from http.server import BaseHTTPRequestHandler


def get_fal_key():
    return os.environ.get("FAL_KEY", "")


def upload_to_fal(image_bytes, filename="wheel.png", content_type="image/png"):
    """Upload image to fal.ai storage."""
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    resp = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=headers,
        json={"content_type": content_type, "file_name": filename}
    )
    if resp.status_code == 200:
        data = resp.json()
        requests.put(data["upload_url"], data=image_bytes, headers={"Content-Type": content_type})
        return data["file_url"]
    return None


def run_birefnet(image_url):
    """Run fal-ai/birefnet for background removal."""
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    submit = requests.post(
        "https://queue.fal.run/fal-ai/birefnet",
        json={"image_url": image_url},
        headers=headers,
        timeout=30
    )
    if submit.status_code != 200:
        return None, f"Submit failed: {submit.status_code}"

    response_url = submit.json().get("response_url")
    if not response_url:
        return None, "No response_url"

    for _ in range(30):
        time.sleep(2)
        r = requests.get(response_url, headers=headers, timeout=30)
        if r.status_code != 200:
            continue
        d = r.json()
        if d.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        # BiRefNet returns image in "image" field
        if "image" in d and d["image"].get("url"):
            return d["image"]["url"], None
        return None, f"Unexpected: {list(d.keys())}"

    return None, "Timeout"


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            image_b64 = data.get("image")
            if not image_b64:
                return self._error(400, "Missing 'image' field")
            if not get_fal_key():
                return self._error(500, "FAL_KEY not configured")

            # Decode
            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_b64)

            # Upload to fal
            uploaded_url = upload_to_fal(image_bytes, "wheel.png", "image/png")
            if not uploaded_url:
                return self._error(500, "Upload to fal.ai failed")

            # Run BiRefNet
            result_url, error = run_birefnet(uploaded_url)
            if error:
                return self._error(500, error)

            # Download result and convert to dataURL so client can use directly
            img_resp = requests.get(result_url, timeout=30)
            if img_resp.status_code != 200:
                return self._error(500, "Could not download result")

            result_b64 = base64.b64encode(img_resp.content).decode()
            data_url = f"data:image/png;base64,{result_b64}"

            self._json({
                "success": True,
                "image": data_url,
                "fal_url": result_url,
            })

        except Exception as e:
            return self._error(500, str(e))

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _error(self, status, message):
        self._json({"success": False, "error": message}, status)
