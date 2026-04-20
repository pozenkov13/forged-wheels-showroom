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
    # Nano Banana Pro (Gemini 3) responds to explicit scene framing.
    # The reference card is labeled "WHEEL DESIGN REFERENCE" — Gemini
    # treats it unambiguously as a reference, not as output content.
    return (
        "The first image is the main photograph of a car. The second image "
        "is a design reference card labeled 'WHEEL DESIGN REFERENCE' — it "
        "shows a wheel rim on gray background. Replace the wheel rims on "
        "the car in the first image with rims that exactly match the design, "
        "spoke pattern, color, finish, and brake caliper color shown in the "
        "reference card. Output the full car photograph with only the wheels "
        "changed — do not output the reference card."
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


def prepare_wheel_reference(wheel_bytes):
    """Compose the wheel PNG into a labeled reference card.

    A/B test (20/04/2026) showed Nano Banana Pro (Gemini 3 Pro Image) outputs
    the reference wheel as a closeup when the two images are ambiguous. Adding
    an explicit "WHEEL DESIGN REFERENCE" text label resolved this — Gemini
    never hallucinates text overlays into the output, so it unambiguously
    treats this as a reference card.

    Output: 700x700 JPEG with gray bg + text label + centered wheel.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return wheel_bytes

    try:
        wheel = Image.open(BytesIO(wheel_bytes))
        if wheel.mode != "RGBA":
            wheel = wheel.convert("RGBA")
        wheel.thumbnail((500, 500), Image.LANCZOS)

        canvas = Image.new("RGB", (700, 700), (64, 64, 64))
        # Center wheel slightly below top to leave room for label
        wx = (700 - wheel.width) // 2
        wy = (700 - wheel.height) // 2 + 30
        canvas.paste(wheel, (wx, wy), wheel)

        # Add label — key signal to Gemini that this is a reference
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        except Exception:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 22)
            except Exception:
                font = ImageFont.load_default()
        label = "WHEEL DESIGN REFERENCE"
        # Compute text width for centering
        try:
            bbox = draw.textbbox((0, 0), label, font=font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 260
        draw.text(((700 - tw) // 2, 20), label, fill=(210, 210, 210), font=font)

        buf = BytesIO()
        canvas.save(buf, format="JPEG", quality=92)
        return buf.getvalue()
    except Exception:
        return wheel_bytes


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


def florence_detect(image_url, target_labels, timeout_s=15):
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
        time.sleep(1)
        poll_resp = requests.get(response_url, headers=headers, timeout=10)
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


def submit_nano_banana_edit(car_url, wheel_url, prompt):
    """Submit Nano Banana Pro (Gemini 3 Pro Image) edit.

    A/B test (20/04) vs FLUX Kontext Max Multi on Tesla Model 3:
    - Kontext: generic multi-spoke wheel (general style, wrong pattern)
    - Nano Banana + labeled reference card: exact Diamond Cut design
      including brake caliper color. Wins on product fidelity.

    The key unlock was the 'WHEEL DESIGN REFERENCE' text label on the
    reference card (see prepare_wheel_reference). Without it, Gemini
    outputs the reference wheel as a closeup instead of the scene.
    """
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
        timeout=20,
    )
    if submit_resp.status_code != 200:
        return None, f"submit_failed_{submit_resp.status_code}"
    response_url = submit_resp.json().get("response_url")
    if not response_url:
        return None, "no_response_url"
    return response_url, None


def poll_fal(response_url):
    """Single poll to fal.ai. Returns (status, data) where status is one of:
    'in_progress', 'completed', 'failed'.

    fal.ai has two URL conventions:
    - Nano Banana: polling response_url returns final result directly when ready
    - FLUX Kontext: must check status_url first, then fetch result_url when COMPLETED
    """
    fal_key = get_fal_key()
    headers = {"Authorization": f"Key {fal_key}"}

    # First check status via /status endpoint (works for all fal.ai queue jobs)
    status_url = response_url.rstrip("/") + "/status"
    try:
        sr = requests.get(status_url, headers=headers, timeout=10)
    except Exception:
        return "in_progress", None
    if sr.status_code != 200:
        return "in_progress", None
    sd = sr.json()
    st = sd.get("status", "")

    if st in ("IN_QUEUE", "IN_PROGRESS", ""):
        return "in_progress", None
    if st in ("FAILED", "ERROR"):
        return "failed", {"error": sd.get("error", "job_failed")}
    if st == "COMPLETED":
        try:
            rr = requests.get(response_url, headers=headers, timeout=10)
            result = rr.json() if rr.content else {}
            if rr.status_code == 200 and "images" in result and result["images"]:
                return "completed", {"result_url": result["images"][0]["url"]}
            # status COMPLETED but no images → validation or model error
            detail = result.get("detail") or result.get("error") or f"unexpected_{list(result.keys())}"
            return "failed", {"error": str(detail)[:200]}
        except Exception as e:
            return "failed", {"error": f"fetch_error: {e}"[:200]}
    return "in_progress", None


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

            # ─────────────────────────────────────────────────────────
            # POLL MODE — client asks "is the job done?"
            # Keeps Vercel invocation under 5s per poll.
            # ─────────────────────────────────────────────────────────
            if data.get("action") == "poll":
                response_url = data.get("response_url")
                if not response_url:
                    return self._error(400, "missing_fields", "response_url required for poll")
                status, info = poll_fal(response_url)
                payload = {"status": status}
                if info:
                    payload.update(info)
                self._json(payload)
                return

            # ─────────────────────────────────────────────────────────
            # SUBMIT MODE — client starts a new wheel swap job
            # ─────────────────────────────────────────────────────────
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
                    "The first image is the main photograph of a car. The second "
                    "image shows a wheel that the user wants installed. Replace "
                    "the wheel rims on the car in the first image with rims that "
                    "exactly match the design, spoke pattern, color, and finish "
                    "of the wheel shown in the second image. Output the full car "
                    "photograph with only the wheels changed."
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
            # Stage 2+3: Single Florence-2 call for BOTH car and wheels
            # (saves ~15s vs running detection twice on Vercel Hobby 60s cap)
            # ─────────────────────────────────────────────────────
            all_labels = {
                "car", "truck", "suv", "vehicle", "van", "pickup truck", "sports car", "sedan",
                "wheel", "tire", "rim", "alloy wheel", "car wheel",
            }
            detected = florence_detect(car_url_full, all_labels, timeout_s=20)
            car_label_set = {"car", "truck", "suv", "vehicle", "van", "pickup truck", "sports car", "sedan"}
            wheel_label_set = {"wheel", "tire", "rim", "alloy wheel", "car wheel"}
            cars = [d for d in detected if d["label"] in car_label_set]
            wheels_found = [d for d in detected if d["label"] in wheel_label_set]

            crop_used = False
            crop_info = None
            car_url_for_gemini = car_url_full

            # Auto-crop only if car takes <70% of frame (screenshot with UI chrome)
            if cars and orig_w and orig_h:
                big = biggest_bbox(cars)
                fill_w = big["w"] / orig_w
                fill_h = big["h"] / orig_h
                if fill_w < 0.70 or fill_h < 0.70:
                    cropped_bytes, cw, ch = crop_to_bbox(image_bytes, big, padding_ratio=0.12)
                    if cropped_bytes and cw and ch:
                        car_url_for_gemini = upload_to_fal(cropped_bytes, "car_cropped.jpg", "image/jpeg")
                        crop_used = True
                        crop_info = {"original": [orig_w, orig_h], "cropped": [cw, ch], "bbox": big}

            soft_warning = None

            # Only HARD reject when Florence finds wheels but NO car — strong
            # signal the user uploaded a wheel-only product shot into the car slot.
            if not cars and wheels_found and not is_custom:
                # Extra safety: the wheels must occupy a large share of the image
                # (otherwise Florence may just have confused UI chrome for wheels).
                big_wheel = biggest_bbox(wheels_found)
                if orig_w and orig_h:
                    fill = (big_wheel["w"] * big_wheel["h"]) / (orig_w * orig_h)
                    if fill > 0.25:
                        return self._error(
                            422, "wheel_instead_of_car",
                            "This looks like a photo of a wheel, not a car. To try a custom wheel, use the WHEEL button on the shelf. To continue here, upload a photo of your car."
                        )

            # Otherwise proceed — Nano Banana Pro is smart enough to handle
            # studio shots and unusual angles even when Florence-2 misses the car.
            if not cars and not wheels_found:
                soft_warning = "We couldn't detect a car with certainty, but we'll try anyway. If the result looks off, try a clearer side view."
            elif cars and not wheels_found:
                soft_warning = "Wheels are hard to see from this angle. If the result looks off, try a side view."

            # ─────────────────────────────────────────────────────
            # Stage 4: Prepare wheel reference (composite on gray bg so
            # Gemini doesn't confuse it with the car scene) + submit
            # ─────────────────────────────────────────────────────
            wheel_ref_bytes = prepare_wheel_reference(wheel_bytes)
            wheel_url = upload_to_fal(wheel_ref_bytes, f"{wheel_id}_ref.jpg", "image/jpeg")

            response_url, error = submit_nano_banana_edit(car_url_for_gemini, wheel_url, prompt)

            if error:
                return self._error(500, "ai_error",
                    "Could not submit AI job. Please try again.")

            self._json({
                "success": True,
                "response_url": response_url,
                "wheel_applied": wheel_display_name,
                "model": "nano-banana-pro/edit",
                "is_custom": is_custom,
                "soft_warning": soft_warning,
                "diagnostics": {
                    "cars_detected": len(cars),
                    "wheels_detected": len(wheels_found),
                    "crop_used": crop_used,
                    "crop_info": crop_info,
                },
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
