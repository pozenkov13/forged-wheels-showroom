#!/usr/bin/env python3
"""
AI Wheel Detection using fal.ai Florence-2 (Object Detection)
Detects wheel positions on car photos for automatic wheel replacement.

This is the CORE INNOVATION for ENISA certification.
Uses Florence-2 Large model for accurate object detection with "wheel" label.
"""

import os
import sys
import json
import time
import requests
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Load API key
env_path = Path(__file__).parent.parent / ".env"
with open(env_path) as f:
    for line in f:
        if line.startswith("FAL_KEY="):
            FAL_KEY = line.strip().split("=", 1)[1]
            break

SCRIPTS_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPTS_DIR.parent
TESTS_DIR = PROJECT_DIR / "generated" / "tests"
TESTS_DIR.mkdir(parents=True, exist_ok=True)


def upload_image_to_fal(image_path: str) -> str:
    """Upload image to fal.ai storage and get URL"""
    print(f"  📤 Uploading image to fal.ai storage...")

    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    ext = Path(image_path).suffix.lower().lstrip('.')
    content_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"

    resp = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=headers,
        json={"content_type": content_type, "file_name": Path(image_path).name}
    )

    if resp.status_code == 200:
        data = resp.json()
        requests.put(data["upload_url"], data=img_bytes, headers={"Content-Type": content_type})
        print(f"  ✅ Uploaded: {data['file_url']}")
        return data["file_url"]

    # Fallback: base64 data URL
    b64 = base64.b64encode(img_bytes).decode()
    return f"data:{content_type};base64,{b64}"


def detect_wheels_florence(image_path: str) -> list:
    """
    Use fal.ai Florence-2 Large for object detection.
    Finds all objects labeled "wheel" in the image.
    Returns list of wheel bounding boxes.
    """
    print(f"\n🔍 AI Wheel Detection (Florence-2)")
    print(f"   Image: {image_path}")

    img = Image.open(image_path)
    img_width, img_height = img.size
    print(f"   Size: {img_width}x{img_height}")

    # Upload image
    image_url = upload_image_to_fal(image_path)

    # Submit to Florence-2 object detection
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "image_url": image_url,
        "task": "object_detection"
    }

    print(f"  🧠 Running Florence-2 object detection...")
    response = requests.post(
        "https://queue.fal.run/fal-ai/florence-2-large/object-detection",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        print(f"  ❌ Queue error: {response.status_code}")
        return []

    queue_data = response.json()
    response_url = queue_data.get("response_url")

    if not response_url:
        print(f"  ❌ No response_url")
        return []

    # Poll for result
    print(f"  ⏳ Waiting for result...")
    for attempt in range(60):
        time.sleep(2)
        result_resp = requests.get(response_url, headers=headers)

        if result_resp.status_code == 200:
            result = result_resp.json()

            if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
                continue

            # Got result - extract wheel bboxes
            if "results" in result and "bboxes" in result["results"]:
                all_bboxes = result["results"]["bboxes"]

                # Florence-2 returns coordinates for a scaled image
                # Get the actual output image size to compute scale
                out_w = result.get("image", {}).get("width", img_width)
                out_h = result.get("image", {}).get("height", img_height)
                scale_x = img_width / out_w
                scale_y = img_height / out_h

                wheels = []
                for bbox in all_bboxes:
                    if bbox.get("label", "").lower() == "wheel":
                        # Scale coordinates back to original image
                        wheels.append({
                            "x": int(bbox["x"] * scale_x),
                            "y": int(bbox["y"] * scale_y),
                            "width": int(bbox["w"] * scale_x),
                            "height": int(bbox["h"] * scale_y),
                            "confidence": 0.85,  # Florence-2 doesn't return scores
                            "label": "wheel"
                        })

                print(f"  ✅ Found {len(wheels)} wheel(s) out of {len(all_bboxes)} objects")
                for i, w in enumerate(wheels):
                    print(f"     Wheel {i+1}: pos=({w['x']},{w['y']}) size={w['width']}x{w['height']}")

                return wheels
            else:
                print(f"  ❌ Unexpected result format: {list(result.keys())}")
                return []

        elif result_resp.status_code == 202:
            continue
        else:
            print(f"  ❌ Poll error: {result_resp.status_code}")
            return []

    print(f"  ❌ Timeout")
    return []


def detect_wheels_simple(image_path: str) -> list:
    """Heuristic fallback when AI is unavailable"""
    img = Image.open(image_path)
    w, h = img.size
    wheel_size = int(w * 0.14)

    return [
        {"x": int(w * 0.15), "y": int(h * 0.65), "width": wheel_size, "height": wheel_size, "confidence": 0.3, "label": "wheel_heuristic"},
        {"x": int(w * 0.72), "y": int(h * 0.65), "width": wheel_size, "height": wheel_size, "confidence": 0.3, "label": "wheel_heuristic"},
    ]


def visualize_detection(image_path: str, wheels: list, output_path: str = None):
    """Draw detection results on image"""
    img = Image.open(image_path).copy()
    draw = ImageDraw.Draw(img)

    for i, wheel in enumerate(wheels):
        x, y, w, h = wheel["x"], wheel["y"], wheel["width"], wheel["height"]
        conf = wheel.get("confidence", 0)

        # Color based on confidence
        if conf > 0.7:
            color = (0, 255, 0)  # Green = AI detected
        elif conf > 0.4:
            color = (255, 255, 0)  # Yellow = medium confidence
        else:
            color = (255, 128, 0)  # Orange = heuristic

        # Draw bounding box
        draw.rectangle([x, y, x + w, y + h], outline=color, width=4)

        # Label
        label = f"Wheel {i+1} ({conf:.0%})"
        draw.text((x + 5, y - 20), label, fill=color)

        # Center crosshair
        cx, cy = x + w // 2, y + h // 2
        draw.line([cx - 10, cy, cx + 10, cy], fill=color, width=2)
        draw.line([cx, cy - 10, cx, cy + 10], fill=color, width=2)

    if output_path is None:
        output_path = str(TESTS_DIR / "detection_result.png")

    img.save(output_path)
    print(f"\n🖼️  Visualization: {output_path}")
    return output_path


def detect_and_visualize(image_path: str) -> dict:
    """Main function: detect wheels and return results with visualization"""
    # Try AI detection
    wheels = detect_wheels_florence(image_path)

    # Fallback to heuristic
    if not wheels:
        print("\n⚠️ AI detection failed, using heuristic fallback")
        wheels = detect_wheels_simple(image_path)

    # Visualize
    viz_path = visualize_detection(image_path, wheels)

    # Build result
    img = Image.open(image_path)
    result = {
        "image": str(image_path),
        "image_size": {"width": img.size[0], "height": img.size[1]},
        "wheels_detected": len(wheels),
        "detection_method": "florence-2" if wheels[0].get("confidence", 0) > 0.5 else "heuristic",
        "wheels": wheels,
        "visualization": viz_path
    }

    # Save JSON
    results_path = TESTS_DIR / "detection_results.json"
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    print("=" * 60)
    print("🔍 FORGED WHEELS — AI Wheel Detector v2 (Florence-2)")
    print("=" * 60)

    # Find test image
    test_images = [
        PROJECT_DIR / "test_car_small.jpg",
        PROJECT_DIR / "uploaded.png",
        PROJECT_DIR / "car_nobg.png",
    ]

    test_img = None
    for img_path in test_images:
        if img_path.exists():
            test_img = str(img_path)
            break

    if not test_img:
        print("❌ No test image found.")
        return

    result = detect_and_visualize(test_img)

    print(f"\n{'='*60}")
    print(f"✅ Detection complete: {result['wheels_detected']} wheels")
    print(f"   Method: {result['detection_method']}")
    for w in result['wheels']:
        print(f"   → ({w['x']},{w['y']}) {w['width']}x{w['height']} conf={w['confidence']:.0%}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
