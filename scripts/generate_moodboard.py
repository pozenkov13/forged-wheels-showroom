#!/usr/bin/env python3
"""Генерация 6 референсных картинок для мудборда Forged через fal.ai Flux Schnell"""
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Загрузка API-ключа
env_file = Path(__file__).parent.parent / '.env'
with open(env_file) as f:
    for line in f:
        if line.startswith('FAL_KEY='):
            FAL_KEY = line.strip().split('=', 1)[1]
            break

API_URL = "https://queue.fal.run/fal-ai/flux/schnell"
OUTPUT_DIR = Path(__file__).parent.parent / 'generated' / 'hero'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 6 референсных промптов для мудборда
MOODBOARD = [
    {
        "name": "01_hero_magazine_cover",
        "prompt": "single luxury forged aluminum wheel on black seamless background, "
                  "5-spoke concave design, brushed titanium finish with polished lip, "
                  "3/4 product view slightly from above, dramatic studio lighting with rim light from top, "
                  "warm gold accent reflection, hyperrealistic commercial photography, "
                  "sharp focus on spokes, 8k resolution, shot on Phase One",
        "size": "square_hd"
    },
    {
        "name": "02_hero_garage_showroom",
        "prompt": "luxurious dark automotive showroom interior at night, "
                  "single black supercar on illuminated podium, "
                  "forged wheel highlighted with focused spotlight, "
                  "architectural ambient lighting, wet concrete floor with reflections, "
                  "cinematic atmosphere, warm gold accent lights, "
                  "minimalist gallery aesthetic, ultra wide angle, 8k",
        "size": "landscape_16_9"
    },
    {
        "name": "03_process_forging",
        "prompt": "close-up macro shot of aluminum billet being forged in industrial press, "
                  "orange hot metal glow, sparks flying, precision machinery, "
                  "dramatic low-key lighting, shallow depth of field, "
                  "commercial manufacturing photography, high detail, 8k",
        "size": "landscape_16_9"
    },
    {
        "name": "04_process_cnc",
        "prompt": "close-up of CNC machine cutting aluminum wheel spoke, "
                  "aluminum chips flying, coolant mist, precision tooling, "
                  "industrial photography, dramatic blue and amber lighting, "
                  "sharp detail of machined surface texture, 8k",
        "size": "landscape_16_9"
    },
    {
        "name": "05_wheel_detail_macro",
        "prompt": "extreme macro close-up of polished forged wheel spoke joining center hub, "
                  "visible brushed aluminum texture, machined details, "
                  "subtle gold color grading, soft rim lighting, "
                  "luxury product photography, ultra sharp focus, 8k",
        "size": "square_hd"
    },
    {
        "name": "06_finishes_comparison",
        "prompt": "four forged aluminum wheel samples arranged in grid, "
                  "brushed titanium, mirror polished chrome, matte black, satin bronze, "
                  "top-down flat lay view, studio lighting, dark background, "
                  "commercial catalog photography, comparison chart style, 8k",
        "size": "square_hd"
    }
]


def submit_request(prompt: str, image_size: str = "square_hd") -> str:
    """Submit generation request, return request_id"""
    data = json.dumps({
        "prompt": prompt,
        "image_size": image_size,
        "num_inference_steps": 4,
        "num_images": 1,
        "enable_safety_checker": True
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Authorization": f"Key {FAL_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
    return result['request_id']


def get_result(request_id: str, max_wait: int = 60) -> dict:
    """Poll for result"""
    result_url = f"https://queue.fal.run/fal-ai/flux/requests/{request_id}"
    for _ in range(max_wait):
        req = urllib.request.Request(
            result_url,
            headers={"Authorization": f"Key {FAL_KEY}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
            if 'images' in data:
                return data
        except urllib.error.HTTPError as e:
            if e.code not in (404, 400):
                raise
        time.sleep(1)
    raise TimeoutError(f"Request {request_id} timed out")


def download_image(url: str, path: Path) -> None:
    urllib.request.urlretrieve(url, path)


def main():
    print(f"🎨 Генерация {len(MOODBOARD)} референсных картинок для мудборда Forged\n")
    results = []

    for i, item in enumerate(MOODBOARD, 1):
        print(f"[{i}/{len(MOODBOARD)}] {item['name']}")
        print(f"   ↳ Submitting...")
        req_id = submit_request(item['prompt'], item['size'])
        print(f"   ↳ Request: {req_id}")

        print(f"   ↳ Waiting for result...")
        result = get_result(req_id)
        img_url = result['images'][0]['url']

        output_path = OUTPUT_DIR / f"{item['name']}.jpg"
        print(f"   ↳ Downloading to {output_path.name}")
        download_image(img_url, output_path)
        print(f"   ✓ Done ({result['timings']['inference']:.2f}s)\n")

        results.append({
            "name": item['name'],
            "path": str(output_path),
            "url": img_url,
            "seed": result['seed']
        })

    # Save manifest
    manifest_path = OUTPUT_DIR / 'manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Готово! Сохранено {len(results)} картинок в {OUTPUT_DIR}")
    print(f"   Манифест: {manifest_path}")
    print(f"   Стоимость: ~${len(results) * 0.003:.3f}")


if __name__ == '__main__':
    main()
