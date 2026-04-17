"""
Vercel Serverless Function — AI Wheel Inpainting
POST /api/inpaint

Accepts: car photo + detected wheel bounding boxes + selected wheel_id
Returns: URL of AI-generated image with wheels replaced

Uses fal.ai Flux Pro v1.1 Fill for photorealistic inpainting.
"""

import os
import json
import base64
import time
import requests
from http.server import BaseHTTPRequestHandler
from pathlib import Path


def get_fal_key():
    """Get fal.ai API key from env vars."""
    return os.environ.get("FAL_KEY", "")


def load_catalog():
    """Load wheel catalog from project root."""
    catalog_path = Path(__file__).parent.parent / "wheels" / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path) as f:
            return json.load(f)
    return []


def build_wheel_prompt(wheel):
    """Build detailed prompt describing target wheel for inpainting."""
    name = wheel.get("name", "forged wheel")
    category = wheel.get("category", "forged")
    finish = wheel.get("finish", "metallic")
    sizes = wheel.get("sizes", ["20"])

    return (
        f"photorealistic {category} forged aluminum alloy car wheel, "
        f"{finish} finish, {sizes[0]}-inch wheel rim, "
        "installed on car, correct perspective, realistic metallic reflections, "
        "sharp detail, professional automotive photography, "
        "seamlessly integrated with car body, correct lighting and shadows"
    )


def create_mask_image(image_width, image_height, wheel_positions):
    """
    Create a mask image with white circles at wheel positions.
    White = area to inpaint, black = keep original.
    Returns PNG bytes.
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    mask = Image.new("RGB", (image_width, image_height), "black")
    draw = ImageDraw.Draw(mask)

    for w in wheel_positions:
        # Expand box by 20% to ensure full wheel coverage
        cx = w["x"] + w["width"] / 2
        cy = w["y"] + w["height"] / 2
        radius = max(w["width"], w["height"]) / 2 * 1.2

        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill="white"
        )

    # Save to bytes
    from io import BytesIO
    buffer = BytesIO()
    mask.save(buffer, format="PNG")
    return buffer.getvalue()


def upload_to_fal(image_bytes, filename, content_type="image/png"):
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

    # Fallback: data URL
    b64 = base64.b64encode(image_bytes).decode()
    return f"data:{content_type};base64,{b64}"


def detect_wheels_florence(image_url):
    """Run Florence-2 object detection to find wheel positions."""
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

    submit_resp = requests.post(
        "https://queue.fal.run/fal-ai/florence-2-large/object-detection",
        json={"image_url": image_url, "task": "object_detection"},
        headers=headers,
        timeout=30
    )

    if submit_resp.status_code != 200:
        return []

    response_url = submit_resp.json().get("response_url")
    if not response_url:
        return []

    for _ in range(25):
        time.sleep(2)
        poll_resp = requests.get(response_url, headers=headers, timeout=30)
        if poll_resp.status_code != 200:
            continue

        result = poll_resp.json()
        if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue

        if "results" in result and "bboxes" in result["results"]:
            bboxes = result["results"]["bboxes"]
            out_w = result.get("image", {}).get("width", 1)
            out_h = result.get("image", {}).get("height", 1)

            wheels = []
            for bbox in bboxes:
                if bbox.get("label", "").lower() == "wheel":
                    wheels.append({
                        "x": bbox["x"],
                        "y": bbox["y"],
                        "width": bbox["w"],
                        "height": bbox["h"],
                        "_source_w": out_w,
                        "_source_h": out_h
                    })
            return wheels

    return []


def run_flux_fill(image_url, mask_url, prompt):
    """Submit Flux Fill job and poll for result."""
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

    # Submit
    submit_resp = requests.post(
        "https://queue.fal.run/fal-ai/flux-pro/v1/fill",
        json={
            "image_url": image_url,
            "mask_url": mask_url,
            "prompt": prompt,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "safety_tolerance": "6"
        },
        headers=headers,
        timeout=30
    )

    if submit_resp.status_code != 200:
        return None, f"Submit failed: {submit_resp.status_code}"

    response_url = submit_resp.json().get("response_url")
    if not response_url:
        return None, "No response_url"

    # Poll (max 90s)
    for _ in range(45):
        time.sleep(2)
        poll_resp = requests.get(response_url, headers=headers, timeout=30)
        if poll_resp.status_code != 200:
            continue

        result = poll_resp.json()
        if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue

        if "images" in result and result["images"]:
            return result["images"][0]["url"], None

        return None, f"Unexpected result: {list(result.keys())}"

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
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            # Extract fields
            image_b64 = data.get("image")  # base64 data URL
            wheel_id = data.get("wheel_id")
            client_wheels = data.get("wheels", [])  # fallback if server detection fails

            if not image_b64 or not wheel_id:
                return self._error(400, "Missing required fields: image, wheel_id")

            if not get_fal_key():
                return self._error(500, "FAL_KEY not configured")

            # Find wheel in catalog
            catalog = load_catalog()
            wheel = next((w for w in catalog if w["id"] == wheel_id), None)
            if not wheel:
                return self._error(404, f"Wheel {wheel_id} not found")

            # Decode image
            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_b64)

            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(image_bytes))
            img_width, img_height = img.size

            # Step 1: Upload image to fal.ai
            image_url = upload_to_fal(image_bytes, "car.png", "image/png")

            # Step 2: Server-side Florence-2 detection (accurate wheel positions)
            detected = detect_wheels_florence(image_url)

            # Scale detected coords back to original image dimensions
            wheel_positions = []
            detection_method = "client"

            if detected:
                sw = detected[0].get("_source_w", img_width)
                sh = detected[0].get("_source_h", img_height)
                scale_x = img_width / sw
                scale_y = img_height / sh
                for w in detected:
                    wheel_positions.append({
                        "x": w["x"] * scale_x,
                        "y": w["y"] * scale_y,
                        "width": w["width"] * scale_x,
                        "height": w["height"] * scale_y
                    })
                detection_method = "florence-2"
            elif client_wheels:
                wheel_positions = client_wheels
            else:
                return self._error(400, "No wheels detected and no client positions provided")

            # Step 3: Create mask with accurate wheel positions
            mask_bytes = create_mask_image(img_width, img_height, wheel_positions)
            if not mask_bytes:
                return self._error(500, "Failed to create mask")

            mask_url = upload_to_fal(mask_bytes, "mask.png", "image/png")

            # Step 4: Build prompt
            prompt = build_wheel_prompt(wheel)

            # Step 5: Run Flux Fill inpainting
            result_url, error = run_flux_fill(image_url, mask_url, prompt)

            if error:
                return self._error(500, error)

            self._json({
                "success": True,
                "result_url": result_url,
                "wheel_applied": wheel["name"],
                "detection_method": detection_method,
                "wheels_found": len(wheel_positions),
                "prompt": prompt
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
