#!/usr/bin/env python3
"""
Regenerate ALL 20 wheels in photorealistic style.
Each wheel: 3/4 angle, real metal textures, studio lighting, transparent background.
"""

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

WHEELS_DIR = Path(__file__).parent.parent / "wheels"
CATALOG_DIR = Path(__file__).parent.parent / "generated" / "catalog"

# Load catalog for wheel data
with open(WHEELS_DIR / "catalog.json") as f:
    catalog = json.load(f)

# Photorealistic prompt template
def make_prompt(wheel):
    name = wheel["name"]
    category = wheel["category"]
    finish = wheel["finish"]

    # Map category to spoke description
    spoke_styles = {
        "monoblock": "clean forged monoblock design with thick solid spokes",
        "concave": "deep concave forged design with elegant curved spokes showing depth",
        "mesh": "intricate mesh pattern with many thin interlocking crossed spokes",
        "split-spoke": "aggressive split-spoke forged design with Y-shaped divided spokes",
        "multi-piece": "3-piece forged construction with visible bolts on the lip and stepped barrel"
    }

    # Map finish to material description
    finish_desc = {
        "brushed": "brushed aluminum with visible machining lines",
        "polished": "mirror polished chrome-like reflective surface",
        "brushed gold": "warm brushed gold anodized finish with subtle metallic sheen",
        "gold": "rich gold painted finish with clear coat shine",
        "silver": "bright silver metallic paint with clear coat",
        "chrome": "deep chrome plating with mirror reflections",
        "matte black": "satin matte black powder coat finish",
        "satin bronze": "warm satin bronze metallic finish",
        "brushed titanium": "titanium-colored brushed metallic finish",
        "polished chrome": "brilliant polished chrome mirror finish",
        "matte black machined": "matte black base with diamond-cut machined spoke faces",
        "satin silver": "soft satin silver metallic finish",
        "polished lip brushed center": "polished mirror lip with brushed silver center",
        "gloss black": "deep gloss black paint with wet-look shine",
        "polished aluminum": "classic polished bare aluminum finish",
        "dark gunmetal": "dark gunmetal grey metallic finish",
        "bronze and black": "two-tone bronze spokes with black barrel",
        "high polish gold rivets": "high polish finish with gold decorative rivets on lip",
        "full matte black": "aggressive full matte black stealth finish",
        "silver diamond cut": "silver base with precision diamond-cut spoke faces"
    }

    spoke = spoke_styles.get(category, "forged aluminum spoke design")
    material = finish_desc.get(finish, f"{finish} metallic finish")

    return f"""Highly realistic product photograph of a single luxury forged aluminum car wheel rim,
{spoke}, {material},
you can see real metal texture and grain on the surface, realistic metallic reflections and highlights
from professional studio softbox lighting, 5-lug bolt pattern with center cap,
the wheel is photographed at a 3/4 angle showing real three-dimensional depth of the barrel lip and spokes,
professional automotive product photography on pure white seamless backdrop,
shot with Canon EOS R5 100mm lens f/8 for maximum sharpness, 8K resolution,
the metal surface looks absolutely REAL with natural imperfections not CGI or rendered"""


def generate_wheel(wheel, headers):
    """Generate one wheel via fal.ai Flux Schnell"""
    prompt = make_prompt(wheel)

    resp = requests.post(
        "https://queue.fal.run/fal-ai/flux/schnell",
        json={
            "prompt": prompt,
            "image_size": "square_hd",
            "num_inference_steps": 4,
            "num_images": 1,
            "enable_safety_checker": False
        },
        headers=headers
    )

    if resp.status_code != 200:
        return None

    response_url = resp.json().get("response_url")
    if not response_url:
        return None

    # Poll for result
    for _ in range(60):
        time.sleep(2)
        r = requests.get(response_url, headers=headers)
        if r.status_code != 200:
            continue
        result = r.json()
        if result.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        if "images" in result and result["images"]:
            return requests.get(result["images"][0]["url"]).content
        return None

    return None


def remove_bg(input_path, output_path):
    """Remove background with rembg"""
    from rembg import remove
    from PIL import Image

    img = Image.open(input_path)
    result = remove(img)
    result.save(output_path, "PNG")


def main():
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }

    print("=" * 60)
    print("🛞 FORGED — Regenerating ALL wheels photorealistic")
    print(f"   {len(catalog)} wheels to process")
    print("=" * 60)

    success = 0
    failed = 0

    for i, wheel in enumerate(catalog):
        wid = wheel["id"]

        # Skip w1 — already done
        if wid == "w1":
            print(f"\n[{i+1}/{len(catalog)}] {wid} ({wheel['name']}) — SKIP (already realistic)")
            success += 1
            continue

        print(f"\n[{i+1}/{len(catalog)}] {wid} ({wheel['name']}) — {wheel['category']} / {wheel['finish']}")

        # Generate
        img_data = generate_wheel(wheel, headers)

        if img_data:
            # Save raw
            raw_path = CATALOG_DIR / f"{wid}_realistic_raw.png"
            raw_path.write_bytes(img_data)
            print(f"  ✅ Generated ({len(img_data)//1024}KB)")

            # Remove background
            final_path = WHEELS_DIR / f"{wid}.png"
            try:
                remove_bg(str(raw_path), str(final_path))
                print(f"  ✅ Background removed → {final_path.name}")
                success += 1
            except Exception as e:
                print(f"  ⚠️ rembg failed: {e}, using raw")
                import shutil
                shutil.copy(str(raw_path), str(final_path))
                success += 1
        else:
            print(f"  ❌ Generation failed")
            failed += 1

        # Small delay
        time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"✅ Done! Success: {success}, Failed: {failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
