"""
Vercel Serverless Function — AI Wheel Inpainting (v2, with auto-crop)
POST /api/inpaint

Pipeline:
  1. Receive car photo (any composition: screenshot, side view, wide shot, etc.)
  2. Preprocess — resize to max 2500px (prevents timeouts on huge uploads)
  3. Florence-2 detects "car" → if found, crop to car bounds with 10% padding
     (this removes UI chrome from screenshots, zooms in on distant cars)
  4. Florence-2 detects "wheel" on the (possibly cropped) image
  5. Nano Banana Pro (Gemini 3 Pro Image) swaps wheels using reference
  6. Return swapped image URL + diagnostic info

Error codes (JSON response):
  "no_car"    — no car visible in image → user should upload a vehicle photo
  "no_wheels" — car detected but wheels not visible → needs side/front-quarter view
  "timeout"   — AI took too long
  "server"    — other backend error
"""

import os
import json
import base64
import time
import requests
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from io import BytesIO


def get_fal_key():
    return os.environ.get("FAL_KEY", "")


def load_catalog():
    catalog_path = Path(__file__).parent.parent / "wheels" / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path) as f:
            return json.load(f)
    return []


def build_wheel_prompt(wheel):
    return (
        "Take the car from image 1. Change both of its wheels to look exactly "
        "like the wheel rim shown in image 2. The car, body color, background, "
        "and lighting must stay identical. Only the wheels change."
    )


def load_wheel_png_bytes(wheel_id):
    wheel_path = Path(__file__).parent.parent / "wheels" / f"{wheel_id}.png"
    if wheel_path.exists():
        with open(wheel_path, "rb") as f:
            return f.read()
    return None


def preprocess_image(image_bytes, max_side=2500):
    """Resize if image is larger than max_side on the long edge.
    Converts to JPEG (smaller payload) and returns bytes + dimensions.
    """
    try:
        from PIL import Image
    except ImportError:
        return image_bytes, None, None

    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        long_side = max(w, h)
        if long_side > max_side:
            scale = max_side / long_side
            new_size = (int(w * scale), int(h * scale))
            img = img.resize(new_size, Image.LANCZOS)
            w, h = img.size
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=92)
        return buf.getvalue(), w, h
    except Exception:
        return image_bytes, None, None


def crop_to_bbox(image_bytes, bbox, padding_ratio=0.10):
    """Crop image to a bounding box with padding (as fraction of bbox size).
    bbox = {"x": int, "y": int, "w": int, "h": int} (absolute pixels).
    """
    try:
        from PIL import Image
    except ImportError:
        return image_bytes, None, None

    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        W, H = img.size
        x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]
        pad_x = int(w * padding_ratio)
        pad_y = int(h * padding_ratio)
        # Bias padding toward bottom (road / wheels more likely to be visible)
        left = max(0, x - pad_x)
        upper = max(0, y - pad_y)
        right = min(W, x + w + pad_x)
        lower = min(H, y + h + int(pad_y * 1.5))
        cropped = img.crop((left, upper, right, lower))
        buf = BytesIO()
        cropped.save(buf, format="JPEG", quality=92)
        return buf.getvalue(), cropped.width, cropped.height
    except Exception:
        return image_bytes, None, None


def upload_to_fal(image_bytes, filename, content_type="image/jpeg"):
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    resp = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=headers,
        json={"content_type": content_type, "file_name": filename},
        timeout=30
    )
    if resp.status_code == 200:
        data = resp.json()
        requests.put(data["upload_url"], data=image_bytes, headers={"Content-Type": content_type})
        return data["file_url"]
    b64 = base64.b64encode(image_bytes).decode()
    return f"data:{content_type};base64,{b64}"


def florence_detect(image_url, target_labels, timeout_s=50):
    """Run Florence-2 object detection. Returns list of dicts with x/y/w/h/label/confidence.
    target_labels: set of lowercase label names to keep (e.g. {"car", "truck", "vehicle"}).
    """
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

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        time.sleep(2)
        poll_resp = requests.get(response_url, headers=headers, timeout=30)
        if poll_resp.status_code != 200:
            continue
        result = poll_resp.json()
        if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        if "results" in result and "bboxes" in result["results"]:
            bboxes = result["results"]["bboxes"]
            out = []
            for bbox in bboxes:
                label = bbox.get("label", "").lower()
                if label in target_labels:
                    out.append({
                        "x": int(bbox["x"]),
                        "y": int(bbox["y"]),
                        "w": int(bbox["w"]),
                        "h": int(bbox["h"]),
                        "label": label,
                    })
            return out
        return []
    return []


def biggest_bbox(bboxes):
    """Return the bbox with the largest area."""
    if not bboxes:
        return None
    return max(bboxes, key=lambda b: b["w"] * b["h"])


def run_nano_banana_edit(car_url, wheel_url, prompt):
    """Nano Banana Pro (Gemini 3 Pro Image) reference-based wheel swap."""
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

    submit_resp = requests.post(
        "https://queue.fal.run/fal-ai/nano-banana-pro/edit",
        json={
            "image_urls": [car_url, wheel_url],
            "prompt": prompt,
            "num_images": 1,
            "output_format": "jpeg",
        },
        headers=headers,
        timeout=30
    )
    if submit_resp.status_code != 200:
        return None, f"submit_failed_{submit_resp.status_code}"

    response_url = submit_resp.json().get("response_url")
    if not response_url:
        return None, "no_response_url"

    deadline = time.time() + 90
    while time.time() < deadline:
        time.sleep(2)
        poll_resp = requests.get(response_url, headers=headers, timeout=30)
        if poll_resp.status_code != 200:
            continue
        result = poll_resp.json()
        if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        if "images" in result and result["images"]:
            return result["images"][0]["url"], None
        return None, f"unexpected_result_{list(result.keys())}"
    return None, "timeout"


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
            wheel_id = data.get("wheel_id")
            custom_wheel_image = data.get("custom_wheel_image")

            if not image_b64 or not wheel_id:
                return self._error(400, "missing_fields", "Missing required fields: image, wheel_id")
            if not get_fal_key():
                return self._error(500, "config", "FAL_KEY not configured")

            # Decode car image
            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_b64)

            # Resolve wheel reference
            is_custom = wheel_id == "custom" and custom_wheel_image
            if is_custom:
                custom_b64 = custom_wheel_image
                if "," in custom_b64:
                    custom_b64 = custom_b64.split(",", 1)[1]
                wheel_bytes = base64.b64decode(custom_b64)
                wheel_display_name = "Your custom wheel"
                prompt = (
                    "Take the car from image 1. Change both of its wheels to look exactly "
                    "like the wheel rim shown in image 2. The car, body color, background, "
                    "and lighting must stay identical. Only the wheels change."
                )
            else:
                catalog = load_catalog()
                wheel = next((w for w in catalog if w["id"] == wheel_id), None)
                if not wheel:
                    return self._error(404, "wheel_not_found", f"Wheel {wheel_id} not found")
                wheel_bytes = load_wheel_png_bytes(wheel_id)
                if not wheel_bytes:
                    return self._error(404, "wheel_png_missing", f"PNG missing for {wheel_id}")
                wheel_display_name = wheel["name"]
                prompt = build_wheel_prompt(wheel)

            # ─────────────────────────────────────────────────────
            # Stage 1: Preprocess (resize if huge)
            # ─────────────────────────────────────────────────────
            image_bytes, orig_w, orig_h = preprocess_image(image_bytes, max_side=2500)

            # Upload car image to fal for detection
            car_url_full = upload_to_fal(image_bytes, "car.jpg", "image/jpeg")

            # ─────────────────────────────────────────────────────
            # Stage 2: Detect "car" (isolates it from UI chrome etc.)
            # ─────────────────────────────────────────────────────
            car_labels = {"car", "truck", "suv", "vehicle", "van", "pickup truck", "sports car", "sedan"}
            cars = florence_detect(car_url_full, car_labels, timeout_s=40)

            crop_used = False
            crop_info = None
            car_url_for_gemini = car_url_full
            current_bytes = image_bytes

            if cars:
                big = biggest_bbox(cars)
                # Only crop if car occupies <70% of image width OR <70% of height
                # (otherwise cropping adds nothing but removes context)
                if orig_w and orig_h:
                    fill_w = big["w"] / orig_w
                    fill_h = big["h"] / orig_h
                    if fill_w < 0.70 or fill_h < 0.70:
                        cropped_bytes, cw, ch = crop_to_bbox(image_bytes, big, padding_ratio=0.12)
                        if cropped_bytes and cw and ch:
                            current_bytes = cropped_bytes
                            car_url_for_gemini = upload_to_fal(cropped_bytes, "car_cropped.jpg", "image/jpeg")
                            crop_used = True
                            crop_info = {"original": [orig_w, orig_h], "cropped": [cw, ch], "bbox": big}

            # ─────────────────────────────────────────────────────
            # Stage 3: Verify wheels are visible (soft check)
            # ─────────────────────────────────────────────────────
            wheel_labels = {"wheel", "tire", "rim", "alloy wheel", "car wheel"}
            wheels_found = florence_detect(car_url_for_gemini, wheel_labels, timeout_s=35)

            if not cars:
                # Hard rule: no car detected → cannot swap wheels INTO nothing.
                # Check if it's a wheel-only image (user confused car vs wheel upload zone).
                if wheels_found and not is_custom:
                    return self._error(
                        422, "wheel_instead_of_car",
                        "This looks like a photo of a wheel, not a car. To try a custom wheel, use the WHEEL button on the shelf. To continue, upload a photo of your car."
                    )
                return self._error(
                    422, "no_car",
                    "We couldn't detect a car in this photo. Please upload a real photo of your vehicle — a clear side view or 3/4 angle works best."
                )

            if cars and not wheels_found:
                # We see a car but no wheels — probably wrong angle (top-down, front-only, cropped)
                # We still try — Gemini is smart — but warn with a soft message in metadata
                soft_warning = "Wheels are hard to see from this angle. If the result looks off, try a side view."
            else:
                soft_warning = None

            # ─────────────────────────────────────────────────────
            # Stage 4: Upload wheel reference + run Gemini swap
            # ─────────────────────────────────────────────────────
            wheel_url = upload_to_fal(wheel_bytes, f"{wheel_id}.png", "image/png")

            result_url, error = run_nano_banana_edit(car_url_for_gemini, wheel_url, prompt)

            if error:
                # Map backend errors to user-friendly codes
                if "timeout" in error:
                    return self._error(504, "timeout",
                        "The AI took too long. This usually means the image is very complex. Try a simpler side-view photo.")
                return self._error(500, "ai_error",
                    "The AI couldn't process this image. Try a different photo or a different wheel.")

            self._json({
                "success": True,
                "result_url": result_url,
                "wheel_applied": wheel_display_name,
                "model": "nano-banana-pro/edit",
                "is_custom": is_custom,
                "soft_warning": soft_warning,
                "diagnostics": {
                    "cars_detected": len(cars),
                    "wheels_detected": len(wheels_found),
                    "crop_used": crop_used,
                    "crop_info": crop_info,
                    "image_resized": orig_w and max(orig_w, orig_h) != max(orig_w, orig_h),
                },
                "prompt": prompt,
            })

        except Exception as e:
            return self._error(500, "server", str(e))

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _error(self, status, code, message):
        self._json({"success": False, "error_code": code, "error": message}, status)
