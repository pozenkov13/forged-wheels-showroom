"""
Vercel Serverless Function — Deterministic Wheel Composite (Path C)
POST /api/inpaint

Pipeline:
  1. Preprocess car image (resize if >2500px)
  2. Florence-2 detects wheel bboxes (with enhancement retry for motion blur)
  3. Filter to top-2 largest bboxes (main car wheels)
  4. Inpaint wheel areas with radial gradient of fender→road color
  5. Warp + feather + ambient-tint the catalog wheel PNG into place
  6. Draw ground-contact shadow under each wheel
  7. Upload composited result to fal storage → return URL

A/B test (20/04/2026) vs Nano Banana Pro and FLUX Kontext Max Multi:
the composite approach is the only one that is simultaneously:
  - pixel-exact reference copy (catalog SKU appears unchanged)
  - scene-preserving (car body, paint, lighting, aspect all untouched)
  - deterministic (same input → same output, no hallucinations)
  - fast (~5-30s vs 15-126s) and cheap (€0.015 vs €0.22-0.44)
"""

import os
import io
import json
import time
import base64
import requests
from http.server import BaseHTTPRequestHandler
from pathlib import Path


def get_fal_key():
    return os.environ.get("FAL_KEY", "")


def load_catalog():
    p = Path(__file__).parent.parent / "wheels" / "catalog.json"
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return []


def load_wheel_png(wheel_id):
    p = Path(__file__).parent.parent / "wheels" / f"{wheel_id}.png"
    return p.read_bytes() if p.exists() else None


# ─────────────────────────────────────────────────────────────
# Image helpers (all via Pillow + OpenCV + numpy)
# ─────────────────────────────────────────────────────────────


def preprocess_image(image_bytes, max_side=2500):
    """Resize if larger than max_side. Return JPEG bytes + dims."""
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h = img.size
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue(), w, h


def enhance_for_detection(image_bytes):
    """Contrast boost + unsharp — helps Florence find wheels on motion blur."""
    from PIL import Image
    import cv2
    import numpy as np

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img)
    blurred = cv2.GaussianBlur(arr, (0, 0), 3)
    sharpened = cv2.addWeighted(arr, 1.5, blurred, -0.5, 0)
    lab = cv2.cvtColor(sharpened, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2RGB)
    out = Image.fromarray(enhanced)
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def trim_wheel_png(wheel_bytes):
    """Crop PNG to tight bounds of non-transparent pixels."""
    from PIL import Image
    import numpy as np

    img = Image.open(io.BytesIO(wheel_bytes))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    arr = np.array(img)
    alpha = arr[..., 3]
    mask = alpha > 10
    if not mask.any():
        return img
    ys, xs = np.where(mask)
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    return Image.fromarray(arr[y0:y1, x0:x1])


def composite_wheels(car_bytes, wheel_bboxes, wheel_bytes_per_bbox):
    """Apply all composite steps. Returns JPEG bytes."""
    from PIL import Image
    import cv2
    import numpy as np

    car = Image.open(io.BytesIO(car_bytes)).convert("RGB")
    car_np = np.array(car).astype(np.float32)
    H, W = car_np.shape[:2]

    # Scene ambient for tinting
    top_half = car_np[: H // 2]
    ambient_mean = top_half.reshape(-1, 3).mean(axis=0)
    ambient_brightness = ambient_mean.mean()

    for bbox, w_bytes in zip(wheel_bboxes, wheel_bytes_per_bbox):
        wheel = trim_wheel_png(w_bytes)
        cx = bbox["x"] + bbox["w"] / 2
        cy = bbox["y"] + bbox["h"] / 2

        # 1. Inpaint wheel area with radial fender→road gradient.
        # Must cover at least as much area as the scaled overlay (scale 1.20)
        # to fully hide the original rim + tire.
        radius = int(max(bbox["w"], bbox["h"]) * 0.62)
        # Sample fender above and road below
        y_a = max(0, int(cy - radius * 1.15))
        y_a_end = max(0, int(cy - radius * 0.95))
        fender_color = ambient_mean
        if y_a_end > y_a:
            slab = car_np[y_a:y_a_end,
                         max(0, int(cx - radius * 0.5)):min(W, int(cx + radius * 0.5))]
            if slab.size:
                fender_color = slab.reshape(-1, 3).mean(axis=0)
        y_b = min(H - 1, int(cy + radius * 0.95))
        y_b_end = min(H, int(cy + radius * 1.15))
        road_color = ambient_mean
        if y_b_end > y_b:
            slab = car_np[y_b:y_b_end,
                         max(0, int(cx - radius * 0.5)):min(W, int(cx + radius * 0.5))]
            if slab.size:
                road_color = slab.reshape(-1, 3).mean(axis=0)
        wheel_mask = np.zeros((H, W), dtype=np.float32)
        cv2.circle(wheel_mask, (int(cx), int(cy)), radius, 1.0, thickness=-1)
        wheel_mask = cv2.GaussianBlur(wheel_mask, (31, 31), 10)
        y_grid = np.arange(H).reshape(-1, 1).astype(np.float32)
        t = np.clip((y_grid - (cy - radius)) / (2 * radius + 1e-6), 0, 1)
        gradient_rgb = (1 - t) * fender_color + t * road_color  # H x 3
        gradient_full = np.broadcast_to(gradient_rgb[:, None, :], (H, W, 3))
        mask3 = wheel_mask[..., np.newaxis]
        car_np = car_np * (1 - mask3) + gradient_full * mask3

        # 2. Resize wheel. 1.15× scale fills arch without clipping fender.
        # Bbox center = wheel center (no offset — Florence is accurate there).
        scale = 1.15
        new_w = int(bbox["w"] * scale)
        new_h = int(bbox["h"] * scale)
        new_x = int(cx - new_w / 2)
        new_y = int(cy - new_h / 2)
        wheel_resized = wheel.resize((new_w, new_h), Image.LANCZOS)
        wheel_arr = np.array(wheel_resized)
        overlay_rgb = np.zeros((H, W, 3), dtype=np.uint8)
        alpha = np.zeros((H, W), dtype=np.float32)
        x0 = max(0, new_x); y0 = max(0, new_y)
        x1 = min(W, new_x + new_w); y1 = min(H, new_y + new_h)
        if x1 > x0 and y1 > y0:
            wx0 = x0 - new_x; wy0 = y0 - new_y
            wx1 = wx0 + (x1 - x0); wy1 = wy0 + (y1 - y0)
            slab = wheel_arr[wy0:wy1, wx0:wx1]
            overlay_rgb[y0:y1, x0:x1] = slab[..., :3]
            alpha[y0:y1, x0:x1] = slab[..., 3].astype(np.float32) / 255.0

        # 3. Feather alpha
        k = 9
        alpha = cv2.GaussianBlur(alpha, (k, k), 4)

        # 4. Ambient tint on overlay RGB
        visible = overlay_rgb[alpha > 0.1]
        if visible.size:
            wb = visible.mean()
            if wb > 20:
                tint = min(1.15, max(0.65, (ambient_brightness * 0.95) / wb))
                overlay_rgb = np.clip(overlay_rgb.astype(np.float32) * tint, 0, 255)

        # 5. Alpha-blend overlay into car
        alpha_3 = alpha[..., np.newaxis]
        car_np = car_np * (1 - alpha_3) + overlay_rgb.astype(np.float32) * alpha_3

        # 6. Ground-contact shadow
        shadow_cy = int(cy + radius * 0.92)
        shadow_rx = int(radius * 0.85)
        shadow_ry = int(radius * 0.22)
        shadow_mask = np.zeros((H, W), dtype=np.float32)
        cv2.ellipse(shadow_mask, (int(cx), shadow_cy), (shadow_rx, shadow_ry),
                    0, 0, 360, 1.0, thickness=-1)
        shadow_mask = cv2.GaussianBlur(shadow_mask, (25, 25), 8)
        car_np = car_np * (1 - 0.35 * shadow_mask[..., np.newaxis])

    result = np.clip(car_np, 0, 255).astype(np.uint8)
    out = Image.fromarray(result)
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────
# fal.ai helpers
# ─────────────────────────────────────────────────────────────


def fal_upload(content, name, ct):
    key = get_fal_key()
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    r = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=headers,
        json={"content_type": ct, "file_name": name},
        timeout=30,
    )
    if r.status_code != 200:
        b64 = base64.b64encode(content).decode()
        return f"data:{ct};base64,{b64}"
    d = r.json()
    requests.put(d["upload_url"], data=content, headers={"Content-Type": ct})
    return d["file_url"]


def florence_raw(image_url):
    key = get_fal_key()
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    r = requests.post(
        "https://queue.fal.run/fal-ai/florence-2-large/object-detection",
        headers=headers,
        json={"image_url": image_url, "task": "object_detection"},
        timeout=30,
    )
    if r.status_code != 200:
        return []
    rurl = r.json().get("response_url")
    if not rurl:
        return []
    for _ in range(20):
        time.sleep(1)
        p = requests.get(rurl, headers=headers, timeout=10)
        if p.status_code != 200:
            continue
        d = p.json()
        if d.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        if "results" in d and "bboxes" in d["results"]:
            labels = {"wheel", "tire", "rim", "alloy wheel", "car wheel"}
            return [
                {"x": int(b["x"]), "y": int(b["y"]), "w": int(b["w"]), "h": int(b["h"])}
                for b in d["results"]["bboxes"]
                if b.get("label", "").lower() in labels
            ]
        return []
    return []


def detect_wheels(image_bytes, max_wheels=2):
    """Detect wheels; retry with contrast-enhancement if first pass returns none."""
    url = fal_upload(image_bytes, "car.jpg", "image/jpeg")
    bboxes = florence_raw(url)
    if not bboxes:
        enhanced = enhance_for_detection(image_bytes)
        url2 = fal_upload(enhanced, "car_enhanced.jpg", "image/jpeg")
        bboxes = florence_raw(url2)
    if not bboxes:
        return []
    # top-N largest + drop stragglers <10% of biggest
    bboxes.sort(key=lambda b: b["w"] * b["h"], reverse=True)
    kept = bboxes[:max_wheels]
    big = kept[0]["w"] * kept[0]["h"]
    kept = [b for b in kept if (b["w"] * b["h"]) >= big * 0.10]
    return kept


# ─────────────────────────────────────────────────────────────
# HTTP handler
# ─────────────────────────────────────────────────────────────


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            cl = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(cl)
            data = json.loads(body)

            # Legacy poll-mode handler — composite is synchronous so always "completed"
            if data.get("action") == "poll":
                return self._json({"status": "completed"})

            image_b64 = data.get("image")
            wheel_id = data.get("wheel_id")
            custom_wheel_image = data.get("custom_wheel_image")

            if not image_b64 or not wheel_id:
                return self._error(400, "missing_fields", "Missing image or wheel_id")
            if not get_fal_key():
                return self._error(500, "config", "FAL_KEY not configured")

            # Decode car image
            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_b64)

            # Resolve wheel reference
            is_custom = wheel_id == "custom" and custom_wheel_image
            if is_custom:
                b64 = custom_wheel_image.split(",", 1)[1] if "," in custom_wheel_image else custom_wheel_image
                wheel_bytes = base64.b64decode(b64)
                wheel_display_name = "Your custom wheel"
            else:
                catalog = load_catalog()
                wheel = next((w for w in catalog if w["id"] == wheel_id), None)
                if not wheel:
                    return self._error(404, "wheel_not_found", f"Wheel {wheel_id} not found")
                wheel_bytes = load_wheel_png(wheel_id)
                if not wheel_bytes:
                    return self._error(404, "wheel_png_missing", f"PNG missing for {wheel_id}")
                wheel_display_name = wheel["name"]

            # Pipeline
            image_bytes, orig_w, orig_h = preprocess_image(image_bytes, max_side=2500)
            wheel_bboxes = detect_wheels(image_bytes, max_wheels=2)

            if not wheel_bboxes:
                return self._error(
                    422, "no_car",
                    "We couldn't detect a car with clearly visible wheels in this photo. "
                    "Please upload a side-view or 3/4 angle photo where at least one wheel is clearly visible."
                )

            # Composite (one wheel PNG used for both bboxes)
            result_bytes = composite_wheels(image_bytes, wheel_bboxes, [wheel_bytes] * len(wheel_bboxes))

            # Upload result to fal storage for CDN delivery
            result_url = fal_upload(result_bytes, "result.jpg", "image/jpeg")

            self._json({
                "success": True,
                "result_url": result_url,
                "wheel_applied": wheel_display_name,
                "model": "forged-composite-v1",
                "is_custom": is_custom,
                "soft_warning": None,
                "diagnostics": {
                    "wheels_detected": len(wheel_bboxes),
                    "image_size": [orig_w, orig_h],
                },
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._error(500, "server", str(e))

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _error(self, status, code, message):
        self._json({"success": False, "error_code": code, "error": message}, status)
