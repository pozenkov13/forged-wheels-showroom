#!/usr/bin/env python3
"""
Generate 12 new forged wheel images for the catalog using fal.ai Flux.
Then remove backgrounds with rembg.
Target: 20 total wheels (8 existing + 12 new)
"""

import os
import json
import time
import requests
from pathlib import Path

# Load API key
env_path = Path(__file__).parent.parent / ".env"
with open(env_path) as f:
    for line in f:
        if line.startswith("FAL_KEY="):
            FAL_KEY = line.strip().split("=", 1)[1]
            break

WHEELS_DIR = Path(__file__).parent.parent / "wheels"
GENERATED_DIR = Path(__file__).parent.parent / "generated" / "catalog"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# 12 new wheel designs to generate
WHEEL_DESIGNS = [
    {
        "id": "w9",
        "name": "Vortex V1",
        "category": "concave",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, deep concave design with 5 thick V-shaped spokes, brushed titanium finish, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "brushed titanium",
        "sizes": ["19", "20", "21"],
        "pcd": ["5x112", "5x120"],
        "et_range": "25-45",
        "price_from": 520,
        "price_to": 780
    },
    {
        "id": "w10",
        "name": "Mesh Pro",
        "category": "mesh",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, intricate mesh pattern with 20 thin crossed spokes, polished chrome finish, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "polished chrome",
        "sizes": ["18", "19", "20"],
        "pcd": ["5x112", "5x114.3"],
        "et_range": "30-45",
        "price_from": 480,
        "price_to": 720
    },
    {
        "id": "w11",
        "name": "Split Star",
        "category": "split-spoke",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, split 10-spoke star pattern, matte black with machined face, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "matte black machined",
        "sizes": ["19", "20", "21", "22"],
        "pcd": ["5x112", "5x120", "5x130"],
        "et_range": "20-45",
        "price_from": 550,
        "price_to": 850
    },
    {
        "id": "w12",
        "name": "Mono Block R",
        "category": "monoblock",
        "prompt": "Professional product photo of a single forged monoblock aluminum car wheel rim, 7 straight thick spokes, satin silver finish, clean minimal design, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "satin silver",
        "sizes": ["18", "19", "20"],
        "pcd": ["5x112", "5x114.3", "5x120"],
        "et_range": "30-50",
        "price_from": 420,
        "price_to": 650
    },
    {
        "id": "w13",
        "name": "Deep Dish GT",
        "category": "multi-piece",
        "prompt": "Professional product photo of a single forged 3-piece deep dish car wheel rim, stepped lip, 6 curved spokes, polished lip with brushed center, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "polished lip brushed center",
        "sizes": ["19", "20", "21"],
        "pcd": ["5x112", "5x120", "5x130"],
        "et_range": "15-40",
        "price_from": 680,
        "price_to": 1100
    },
    {
        "id": "w14",
        "name": "Aero Flow",
        "category": "concave",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, aerodynamic flowing 8-spoke design with slight twist, gloss black finish, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "gloss black",
        "sizes": ["19", "20", "21", "22"],
        "pcd": ["5x112", "5x114.3", "5x120"],
        "et_range": "25-45",
        "price_from": 490,
        "price_to": 750
    },
    {
        "id": "w15",
        "name": "Classic Ten",
        "category": "monoblock",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, classic 10-spoke design, polished aluminum finish, timeless elegant style, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "polished aluminum",
        "sizes": ["18", "19", "20"],
        "pcd": ["5x112", "5x114.3"],
        "et_range": "30-45",
        "price_from": 400,
        "price_to": 600
    },
    {
        "id": "w16",
        "name": "Carbon Weave",
        "category": "mesh",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, fine mesh weave pattern, carbon fiber look with dark gunmetal finish, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "dark gunmetal",
        "sizes": ["20", "21", "22"],
        "pcd": ["5x112", "5x120", "5x130"],
        "et_range": "20-40",
        "price_from": 620,
        "price_to": 950
    },
    {
        "id": "w17",
        "name": "RS Forged",
        "category": "split-spoke",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, aggressive split 5-spoke design, two-tone bronze and black finish, motorsport inspired, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "bronze and black",
        "sizes": ["19", "20", "21"],
        "pcd": ["5x112", "5x114.3", "5x120"],
        "et_range": "25-45",
        "price_from": 560,
        "price_to": 870
    },
    {
        "id": "w18",
        "name": "Luxury Plus",
        "category": "multi-piece",
        "prompt": "Professional product photo of a single forged 2-piece aluminum car wheel rim, 12 thin elegant spokes, high polish finish with gold rivets on lip, luxury style, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "high polish gold rivets",
        "sizes": ["20", "21", "22"],
        "pcd": ["5x112", "5x120", "5x130"],
        "et_range": "15-35",
        "price_from": 750,
        "price_to": 1200
    },
    {
        "id": "w19",
        "name": "Stealth X",
        "category": "concave",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, deep concave with 6 wide spokes, full matte black stealth finish, aggressive stance look, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "full matte black",
        "sizes": ["20", "21", "22"],
        "pcd": ["5x112", "5x114.3", "5x120", "5x130"],
        "et_range": "20-40",
        "price_from": 530,
        "price_to": 820
    },
    {
        "id": "w20",
        "name": "Touring Classic",
        "category": "monoblock",
        "prompt": "Professional product photo of a single forged aluminum car wheel rim, classic 5-spoke touring design, silver with diamond cut face, understated luxury, studio lighting on pure white background, ultra sharp, 4K, photorealistic, no car, isolated wheel only",
        "finish": "silver diamond cut",
        "sizes": ["18", "19", "20"],
        "pcd": ["5x112", "5x114.3"],
        "et_range": "35-50",
        "price_from": 380,
        "price_to": 580
    }
]


def generate_wheel_image(design: dict) -> str:
    """Generate a wheel image using fal.ai Flux Schnell (queue mode)"""
    print(f"\n🛞 Generating {design['name']} ({design['category']})...")

    url = "https://queue.fal.run/fal-ai/flux/schnell"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": design["prompt"],
        "image_size": "square_hd",
        "num_inference_steps": 4,
        "num_images": 1,
        "enable_safety_checker": False
    }

    # Submit to queue
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"  ❌ Queue error: {response.status_code} - {response.text[:200]}")
        return None

    queue_data = response.json()
    response_url = queue_data.get("response_url")
    if not response_url:
        print(f"  ❌ No response_url in queue response")
        return None

    print(f"  ⏳ Queued, waiting for result...")

    # Poll for result
    for attempt in range(60):  # max 60 attempts × 2s = 120s
        time.sleep(2)
        result_resp = requests.get(response_url, headers=headers)

        if result_resp.status_code == 200:
            result = result_resp.json()

            # Check if still in queue
            if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
                pos = result.get("queue_position", "?")
                print(f"  ⏳ Still processing... (queue pos: {pos})", end="\r")
                continue

            # Got result
            if "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]

                # Download image
                img_response = requests.get(image_url)
                output_path = GENERATED_DIR / f"{design['id']}_raw.png"
                with open(output_path, "wb") as f:
                    f.write(img_response.content)

                print(f"  ✅ Saved raw image: {output_path}")
                return str(output_path)
            else:
                print(f"  ❌ No images in result: {list(result.keys())}")
                return None
        elif result_resp.status_code == 202:
            # Still processing
            continue
        else:
            print(f"  ❌ Poll error: {result_resp.status_code}")
            return None

    print(f"  ❌ Timeout waiting for result")
    return None


def remove_background(input_path: str, output_path: str) -> bool:
    """Remove background using rembg"""
    try:
        from rembg import remove
        from PIL import Image

        print(f"  🔧 Removing background...")
        input_img = Image.open(input_path)
        output_img = remove(input_img)
        output_img.save(output_path, "PNG")
        print(f"  ✅ Saved: {output_path}")
        return True
    except ImportError:
        print("  ⚠️ rembg not installed. Run: pip install rembg")
        return False


def save_catalog_data():
    """Save wheel catalog as JSON for frontend"""
    catalog = []

    # Existing wheels (w1-w8) with basic data
    existing = [
        {"id": "w1", "name": "HRE S101", "category": "monoblock", "finish": "brushed", "sizes": ["19", "20", "21"], "pcd": ["5x112", "5x120"], "et_range": "25-45", "price_from": 500, "price_to": 750, "image": "wheels/w1.png"},
        {"id": "w2", "name": "Vossen CV3", "category": "concave", "finish": "polished", "sizes": ["19", "20"], "pcd": ["5x112", "5x114.3"], "et_range": "30-45", "price_from": 480, "price_to": 700, "image": "wheels/w2.png"},
        {"id": "w3", "name": "ADV.1 Gold", "category": "concave", "finish": "brushed gold", "sizes": ["20", "21"], "pcd": ["5x112", "5x120"], "et_range": "25-40", "price_from": 550, "price_to": 820, "image": "wheels/w3.png"},
        {"id": "w4", "name": "Classic Gold", "category": "monoblock", "finish": "gold", "sizes": ["18", "19", "20"], "pcd": ["5x112", "5x114.3"], "et_range": "30-50", "price_from": 430, "price_to": 650, "image": "wheels/w4.png"},
        {"id": "w5", "name": "Silver Multi", "category": "multi-piece", "finish": "silver", "sizes": ["19", "20"], "pcd": ["5x112", "5x120"], "et_range": "25-45", "price_from": 600, "price_to": 900, "image": "wheels/w5.png"},
        {"id": "w6", "name": "Chrome Deep", "category": "multi-piece", "finish": "chrome", "sizes": ["20", "21", "22"], "pcd": ["5x112", "5x120", "5x130"], "et_range": "20-40", "price_from": 700, "price_to": 1100, "image": "wheels/w6.png"},
        {"id": "w7", "name": "Matte Stealth", "category": "monoblock", "finish": "matte black", "sizes": ["19", "20", "21"], "pcd": ["5x112", "5x114.3", "5x120"], "et_range": "25-45", "price_from": 460, "price_to": 700, "image": "wheels/w7.png"},
        {"id": "w8", "name": "Bronze Flow", "category": "concave", "finish": "satin bronze", "sizes": ["20", "21"], "pcd": ["5x112", "5x120"], "et_range": "25-40", "price_from": 520, "price_to": 800, "image": "wheels/w8.png"},
    ]
    catalog.extend(existing)

    # New generated wheels
    for design in WHEEL_DESIGNS:
        wheel_file = f"wheels/{design['id']}.png"
        catalog.append({
            "id": design["id"],
            "name": design["name"],
            "category": design["category"],
            "finish": design["finish"],
            "sizes": design["sizes"],
            "pcd": design["pcd"],
            "et_range": design["et_range"],
            "price_from": design["price_from"],
            "price_to": design["price_to"],
            "image": wheel_file
        })

    catalog_path = Path(__file__).parent.parent / "wheels" / "catalog.json"
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"\n📋 Catalog saved: {catalog_path} ({len(catalog)} wheels)")


def main():
    print("=" * 60)
    print("🛞 FORGED WHEELS — Catalog Generator")
    print(f"   Generating {len(WHEEL_DESIGNS)} new wheels")
    print(f"   Using fal.ai Flux Schnell")
    print("=" * 60)

    success = 0
    failed = 0

    for design in WHEEL_DESIGNS:
        raw_path = generate_wheel_image(design)

        if raw_path:
            # Remove background
            final_path = WHEELS_DIR / f"{design['id']}.png"
            if remove_background(raw_path, str(final_path)):
                success += 1
            else:
                # If rembg fails, copy raw as fallback
                import shutil
                shutil.copy(raw_path, str(final_path))
                success += 1
                print(f"  ⚠️ Using raw image (no bg removal)")
        else:
            failed += 1

        # Small delay to avoid rate limiting
        time.sleep(1)

    # Save catalog data
    save_catalog_data()

    print("\n" + "=" * 60)
    print(f"✅ Done! Generated: {success}, Failed: {failed}")
    print(f"Total wheels in catalog: {8 + success}")
    print("=" * 60)


if __name__ == "__main__":
    main()
