"""
Path C prototype — 3D composite wheel swap using classical CV.

Pipeline:
  1. Florence-2 detects wheels → bboxes (via fal.ai)
  2. Auto-crop wheel PNG to trim transparent padding
  3. Resize + warp wheel to fit each detected bbox
  4. Feather alpha edges + alpha-blend over original photo

Usage:
  python3 scripts/composite_wheels.py <car_image> <wheel_id> [output.jpg]

Example:
  python3 scripts/composite_wheels.py ~/Desktop/tesla.png w10 /tmp/result.jpg
"""

import os
import io
import sys
import time
import base64
import requests
from pathlib import Path

import numpy as np
import cv2
from PIL import Image


ROOT = Path(__file__).parent.parent


def load_fal_key():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("FAL_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("FAL_KEY", "")


FAL_KEY = load_fal_key()


def fal_upload(content, name, ct):
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    r = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=headers,
        json={"content_type": ct, "file_name": name},
        timeout=30,
    )
    r.raise_for_status()
    d = r.json()
    requests.put(d["upload_url"], data=content, headers={"Content-Type": ct}).raise_for_status()
    return d["file_url"]


def _florence_raw(image_url):
    """Single Florence-2 call, returns all wheel bboxes (unfiltered)."""
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    submit = requests.post(
        "https://queue.fal.run/fal-ai/florence-2-large/object-detection",
        headers=headers,
        json={"image_url": image_url, "task": "object_detection"},
        timeout=30,
    )
    submit.raise_for_status()
    rurl = submit.json()["response_url"]
    for _ in range(20):
        time.sleep(1)
        r = requests.get(rurl, headers=headers, timeout=10)
        if r.status_code != 200:
            continue
        d = r.json()
        if d.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        if "results" in d and "bboxes" in d["results"]:
            wheel_labels = {"wheel", "tire", "rim", "alloy wheel", "car wheel"}
            return [
                {"x": int(b["x"]), "y": int(b["y"]), "w": int(b["w"]), "h": int(b["h"])}
                for b in d["results"]["bboxes"]
                if b.get("label", "").lower() in wheel_labels
            ]
        break
    return []


def preprocess_for_detection(image_bytes):
    """Contrast-boost + sharpening pass for motion-blurred photos
    (Mercedes action shots etc.) — helps Florence detect wheels.
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img)
    # Unsharp mask
    blurred = cv2.GaussianBlur(arr, (0, 0), 3)
    sharpened = cv2.addWeighted(arr, 1.5, blurred, -0.5, 0)
    # Contrast boost
    lab = cv2.cvtColor(sharpened, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    out = Image.fromarray(enhanced)
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def florence_detect_wheels(image_bytes, max_wheels=2):
    """Return up to max_wheels largest bboxes (filters background cars).
    If first pass finds 0, retries with contrast-enhanced image.
    """
    url = fal_upload(image_bytes, "car.jpg", "image/jpeg")
    bboxes = _florence_raw(url)

    # Retry with preprocessing if empty
    if not bboxes:
        print(f"  [retry] Florence found 0 — retrying with enhanced image...")
        enhanced = preprocess_for_detection(image_bytes)
        url2 = fal_upload(enhanced, "car_enhanced.jpg", "image/jpeg")
        bboxes = _florence_raw(url2)

    if not bboxes:
        return []

    # Keep only top-N largest (by area) — filters background cars / tiny false positives
    bboxes.sort(key=lambda b: b["w"] * b["h"], reverse=True)
    kept = bboxes[:max_wheels]

    # Further sanity: drop bboxes < 10% of the largest (tiny stragglers)
    if kept:
        biggest_area = kept[0]["w"] * kept[0]["h"]
        kept = [b for b in kept if (b["w"] * b["h"]) >= biggest_area * 0.10]

    return kept


def trim_png_to_wheel(wheel_png_bytes):
    """Crop the PNG to tight bounds of the non-transparent pixels (wheel only),
    removing the transparent padding PowerWheels adds around the wheel.
    """
    img = Image.open(io.BytesIO(wheel_png_bytes))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    arr = np.array(img)
    alpha = arr[..., 3]
    # Find bounds of alpha > small threshold
    mask = alpha > 10
    if not mask.any():
        return img
    ys, xs = np.where(mask)
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    return Image.fromarray(arr[y0:y1, x0:x1])


def warp_wheel_into_bbox(wheel_rgba_pil, bbox, img_shape, scale=1.15):
    """Resize wheel to match bbox and return (overlay_rgb, alpha_mask) in
    full-image canvas coordinates.

    scale: multiplier applied to bbox size before placing wheel PNG.
           Florence-2 bbox usually wraps the rim only — not the tire.
           Scale 1.15-1.22 expands the overlay to cover the tire area too.

    img_shape is (H, W) of the target canvas.
    """
    H, W = img_shape[:2]
    x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]

    cx = x + w / 2
    cy = y + h / 2
    new_w = int(w * scale)
    new_h = int(h * scale)
    new_x = int(cx - new_w / 2)
    new_y = int(cy - new_h / 2)

    wheel_resized = wheel_rgba_pil.resize((new_w, new_h), Image.LANCZOS)
    wheel_arr = np.array(wheel_resized)  # H x W x 4

    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    alpha = np.zeros((H, W), dtype=np.float32)

    # Clip to canvas (using expanded coords)
    x0 = max(0, new_x); y0 = max(0, new_y)
    x1 = min(W, new_x + new_w); y1 = min(H, new_y + new_h)
    wx0 = x0 - new_x; wy0 = y0 - new_y
    wx1 = wx0 + (x1 - x0); wy1 = wy0 + (y1 - y0)

    if x1 > x0 and y1 > y0:
        slab = wheel_arr[wy0:wy1, wx0:wx1]
        rgb[y0:y1, x0:x1] = slab[..., :3]
        alpha[y0:y1, x0:x1] = slab[..., 3].astype(np.float32) / 255.0

    return rgb, alpha


def feather_alpha(alpha, sigma=3):
    """Soft edges so blend is smooth."""
    # Dilate slightly then Gaussian blur
    k = int(max(3, sigma * 2)) | 1  # odd kernel
    return cv2.GaussianBlur(alpha, (k, k), sigma)


def composite(car_bytes, wheel_id):
    """Main entry point — takes car bytes + wheel_id from catalog, returns JPEG bytes."""
    t0 = time.time()

    # Detect wheels
    print(f"[{time.time()-t0:.1f}s] Detecting wheels via Florence-2...")
    wheel_bboxes = florence_detect_wheels(car_bytes)
    print(f"[{time.time()-t0:.1f}s] Found {len(wheel_bboxes)} wheels: {wheel_bboxes}")

    if not wheel_bboxes:
        print("No wheels detected; aborting.")
        return None

    # Load catalog wheel PNG
    wheel_path = ROOT / "wheels" / f"{wheel_id}.png"
    wheel_bytes = wheel_path.read_bytes()
    wheel_trimmed = trim_png_to_wheel(wheel_bytes)
    print(f"[{time.time()-t0:.1f}s] Wheel PNG trimmed: {wheel_trimmed.size}")

    # Load car
    car = Image.open(io.BytesIO(car_bytes)).convert("RGB")
    car_np = np.array(car).astype(np.float32)
    H, W = car_np.shape[:2]

    # Sample ambient scene color (from top-half of car) for wheel tinting later
    top_half = car_np[: H // 2]
    ambient_mean = top_half.reshape(-1, 3).mean(axis=0)  # average scene RGB
    ambient_brightness = ambient_mean.mean()

    # Composite each wheel
    for bbox in wheel_bboxes:
        cx = bbox["x"] + bbox["w"] / 2
        cy = bbox["y"] + bbox["h"] / 2

        # Step 1: INPAINT the original wheel area with surrounding colors.
        # Take a thin ring of pixels just OUTSIDE the wheel (fender above,
        # road below) and fill the wheel region with a radial blend so the
        # original wheel vanishes before we overlay the new one.
        radius = int(max(bbox["w"], bbox["h"]) * 0.55)
        inner_r = int(radius * 0.80)

        # Sample color ABOVE the wheel (fender / car body)
        y_above = max(0, int(cy - radius * 1.15))
        y_above_end = max(0, int(cy - radius * 0.95))
        if y_above_end > y_above:
            fender_sample = car_np[y_above:y_above_end,
                                   max(0, int(cx - radius * 0.5)):min(W, int(cx + radius * 0.5))]
            fender_color = fender_sample.reshape(-1, 3).mean(axis=0) if fender_sample.size else ambient_mean
        else:
            fender_color = ambient_mean

        # Sample color BELOW (road/ground)
        y_below = min(H - 1, int(cy + radius * 0.95))
        y_below_end = min(H, int(cy + radius * 1.15))
        if y_below_end > y_below:
            road_sample = car_np[y_below:y_below_end,
                                 max(0, int(cx - radius * 0.5)):min(W, int(cx + radius * 0.5))]
            road_color = road_sample.reshape(-1, 3).mean(axis=0) if road_sample.size else ambient_mean
        else:
            road_color = ambient_mean

        # Paint radial gradient inside wheel circle: fender at top, road at bottom
        # Create a circular mask for the wheel area
        wheel_mask = np.zeros((H, W), dtype=np.float32)
        cv2.circle(wheel_mask, (int(cx), int(cy)), radius, 1.0, thickness=-1)
        wheel_mask = cv2.GaussianBlur(wheel_mask, (31, 31), 10)

        # Vertical gradient from fender (top) to road (bottom) within bbox
        y_grid = np.arange(H).reshape(-1, 1).astype(np.float32)
        t = np.clip((y_grid - (cy - radius)) / (2 * radius + 1e-6), 0, 1)  # H x 1
        gradient_rgb = (1 - t) * fender_color + t * road_color  # H x 3 via broadcast
        gradient_full = np.broadcast_to(gradient_rgb[:, None, :], (H, W, 3))

        mask3 = wheel_mask[..., np.newaxis]
        car_np = car_np * (1 - mask3) + gradient_full * mask3

        # Step 2: overlay new wheel with feathered alpha
        overlay_rgb, alpha = warp_wheel_into_bbox(wheel_trimmed, bbox, (H, W))
        alpha = feather_alpha(alpha, sigma=4)

        # Step 3: tint the wheel RGB to match scene ambient brightness.
        # Wheel PNGs are studio-lit (~180-220 brightness). If scene is darker,
        # we multiply wheel pixels to harmonize.
        wheel_visible = overlay_rgb[alpha > 0.1]
        if wheel_visible.size:
            wheel_brightness = wheel_visible.mean()
            if wheel_brightness > 20:
                # Target: match scene ambient with slight offset (wheels typically brighter)
                tint_factor = min(1.15, max(0.65, (ambient_brightness * 0.95) / wheel_brightness))
                overlay_rgb = np.clip(overlay_rgb.astype(np.float32) * tint_factor, 0, 255)

        alpha_3 = alpha[..., np.newaxis]
        car_np = car_np * (1 - alpha_3) + overlay_rgb.astype(np.float32) * alpha_3

        # Step 4: ground-contact shadow below wheel for natural integration
        shadow_cy = int(cy + radius * 0.92)
        shadow_rx = int(radius * 0.85)
        shadow_ry = int(radius * 0.22)
        shadow_mask = np.zeros((H, W), dtype=np.float32)
        cv2.ellipse(shadow_mask, (int(cx), shadow_cy), (shadow_rx, shadow_ry),
                    0, 0, 360, 1.0, thickness=-1)
        shadow_mask = cv2.GaussianBlur(shadow_mask, (25, 25), 8)
        # Multiplicative shadow — darkens ground by ~30%
        shadow_strength = 0.35
        car_np = car_np * (1 - shadow_strength * shadow_mask[..., np.newaxis])

    print(f"[{time.time()-t0:.1f}s] Composite done.")

    result = np.clip(car_np, 0, 255).astype(np.uint8)
    out = Image.fromarray(result)
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def main():
    if len(sys.argv) < 3:
        print("Usage: composite_wheels.py <car_image> <wheel_id> [output.jpg]")
        sys.exit(1)

    car_path = Path(sys.argv[1]).expanduser()
    wheel_id = sys.argv[2]
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(f"/tmp/composite_{wheel_id}.jpg")

    car_bytes = car_path.read_bytes()
    result = composite(car_bytes, wheel_id)
    if result:
        out_path.write_bytes(result)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
