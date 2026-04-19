#!/usr/bin/env python3
"""
Test: OmniGen-based wheel replacement
Input:  car photo + reference wheel image
Output: photorealistic wheel swap

Uses fal-ai/omnigen-v1 — multimodal model that accepts multiple
reference images and blends them per prompt instructions.
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path

# Load API key
env_path = Path(__file__).parent.parent / ".env"
with open(env_path) as f:
    for line in f:
        if line.startswith("FAL_KEY="):
            FAL_KEY = line.strip().split("=", 1)[1]
            break

PROJECT = Path(__file__).parent.parent
OUT_DIR = PROJECT / "generated" / "tests"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Inputs
CAR_PHOTO = PROJECT / "test_car_small.jpg"
WHEEL_REFERENCE = PROJECT / "wheels" / "w17.png"  # RS Forged, bronze/black

HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}


def upload_to_fal(file_path: Path) -> str:
    """Upload image to fal.ai storage and return URL."""
    print(f"  📤 Uploading {file_path.name}...")

    ext = file_path.suffix.lower().lstrip(".")
    content_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"

    resp = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=HEADERS,
        json={"content_type": content_type, "file_name": file_path.name},
    )

    if resp.status_code != 200:
        print(f"  ❌ Upload init failed: {resp.status_code}")
        return None

    data = resp.json()
    with open(file_path, "rb") as f:
        requests.put(data["upload_url"], data=f.read(), headers={"Content-Type": content_type})

    print(f"  ✅ Uploaded: {data['file_url']}")
    return data["file_url"]


def run_omnigen(car_url: str, wheel_url: str, out_path: Path):
    """Run OmniGen with car + wheel reference."""
    print(f"\n🎨 Running OmniGen...")

    payload = {
        "prompt": (
            "Replace both wheels of the car shown in the first image <img><|image_1|></img> "
            "with the exact wheel design shown in the second image <img><|image_2|></img>. "
            "The new wheels must match the car's perspective, angle, size, and lighting. "
            "Keep the car body, color, reflections, and background completely unchanged. "
            "The replacement wheels should fit precisely inside the wheel arches with realistic "
            "metallic reflections and proper shadows under the car. Photorealistic result."
        ),
        "input_images": [car_url, wheel_url],
        "guidance_scale": 2.5,
        "image_guidance_scale": 1.6,
        "num_inference_steps": 50,
        "img_guidance_scale": 1.6,
    }

    resp = requests.post(
        "https://queue.fal.run/fal-ai/omnigen-v1",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"  ❌ Submit failed: {resp.status_code}")
        print(f"     {resp.text[:500]}")
        return False

    response_url = resp.json().get("response_url")
    print(f"  ⏳ Queued, waiting for result (up to 3 min)...")

    for i in range(90):  # max 3 min
        time.sleep(2)
        r = requests.get(response_url, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            continue

        data = r.json()
        status = data.get("status")

        if status in ("IN_QUEUE", "IN_PROGRESS"):
            if i % 10 == 0:
                pos = data.get("queue_position", "?")
                print(f"     ({i*2}s) status={status} pos={pos}")
            continue

        # Got result
        if "images" in data and data["images"]:
            img_url = data["images"][0]["url"]
            print(f"  ✅ Got result: {img_url}")

            # Download immediately (URLs expire)
            img_data = requests.get(img_url, timeout=60).content
            out_path.write_bytes(img_data)
            print(f"  💾 Saved: {out_path} ({len(img_data) // 1024}KB)")
            return True
        else:
            print(f"  ❌ Unexpected response keys: {list(data.keys())}")
            print(f"     {json.dumps(data, indent=2)[:500]}")
            return False

    print(f"  ❌ Timeout after 3 min")
    return False


def run_omnigen_alt_format(car_url: str, wheel_url: str, out_path: Path):
    """Fallback with different prompt format if first doesn't work."""
    print(f"\n🎨 Trying alternative OmniGen prompt format...")

    payload = {
        "prompt": (
            "A car from the reference image with its wheels replaced by the wheels "
            "from the second reference image. The car keeps all original features: "
            "body color, shape, position, background, lighting. Only the wheels are "
            "changed to match the design in the second reference. Photorealistic, "
            "perfect integration, correct perspective and shadows."
        ),
        "input_image_urls": [car_url, wheel_url],
        "image_size": "landscape_4_3",
        "num_inference_steps": 50,
    }

    resp = requests.post(
        "https://queue.fal.run/fal-ai/omnigen-v1",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:300]}")


def main():
    print("=" * 60)
    print("🛞 OmniGen Wheel Swap Test")
    print("=" * 60)

    if not CAR_PHOTO.exists():
        print(f"❌ Car photo not found: {CAR_PHOTO}")
        return
    if not WHEEL_REFERENCE.exists():
        print(f"❌ Wheel reference not found: {WHEEL_REFERENCE}")
        return

    print(f"\n📸 Car photo: {CAR_PHOTO.name}")
    print(f"🛞 Wheel reference: {WHEEL_REFERENCE.name}")

    # Upload both
    print("\n📤 Uploading to fal.ai storage...")
    car_url = upload_to_fal(CAR_PHOTO)
    wheel_url = upload_to_fal(WHEEL_REFERENCE)

    if not car_url or not wheel_url:
        print("❌ Upload failed")
        return

    # Run OmniGen
    output = OUT_DIR / "omnigen_wheel_swap_result.jpg"
    success = run_omnigen(car_url, wheel_url, output)

    if not success:
        print("\n🔄 First attempt failed, trying alternative format...")
        run_omnigen_alt_format(car_url, wheel_url, output)

    if output.exists():
        print(f"\n{'='*60}")
        print(f"✅ DONE — Result saved to: {output}")
        print(f"   Open in Finder: open {output}")
        print(f"{'='*60}")
    else:
        print(f"\n❌ No result file produced")


if __name__ == "__main__":
    main()
