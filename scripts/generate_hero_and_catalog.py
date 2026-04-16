#!/usr/bin/env python3
"""Генерирует hero-диск (без текста) + 3 диска для каталога.
Автоматически убирает фон через rembg."""
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from rembg import remove

# Загрузка API-ключа
env_file = Path(__file__).parent.parent / '.env'
with open(env_file) as f:
    for line in f:
        if line.startswith('FAL_KEY='):
            FAL_KEY = line.strip().split('=', 1)[1]
            break

API_URL = "https://queue.fal.run/fal-ai/flux/schnell"
HERO_DIR = Path(__file__).parent.parent / 'generated' / 'hero'
CATALOG_DIR = Path(__file__).parent.parent / 'generated' / 'catalog'
HERO_DIR.mkdir(parents=True, exist_ok=True)
CATALOG_DIR.mkdir(parents=True, exist_ok=True)

# КРИТИЧНО: "no text, no logos, no branding, no letters, blank center cap"
# в каждом промпте, чтобы AI не дорисовывал надписи на хабе
NO_TEXT = "no text, no logo, no letters, no branding, no writing, blank clean center cap, "

WHEELS = [
    # Hero — элегантный бронзовый 5-спицевый concave
    {
        "output_dir": HERO_DIR,
        "name": "02_hero_bronze_concave",
        "prompt": NO_TEXT +
                  "single luxury forged aluminum wheel, 20 inch concave 5-spoke design, "
                  "satin bronze finish with polished outer lip, "
                  "3/4 product view from slightly above, "
                  "dramatic studio lighting with warm rim light from top-right, "
                  "seamless pure black background, hyperrealistic commercial photography, "
                  "sharp focus on every spoke, subtle reflections, 8k resolution",
        "size": "square_hd"
    },
    # Catalog 1 — Concave V1: 5-spoke brushed titanium
    {
        "output_dir": CATALOG_DIR,
        "name": "wheel_01_concave_v1",
        "prompt": NO_TEXT +
                  "luxury forged monoblock wheel, deep concave 5-spoke design, "
                  "brushed titanium finish, polished lip, "
                  "straight 3/4 product view, studio lighting, "
                  "seamless black background, commercial catalog photography, "
                  "hyperrealistic, sharp detail, 8k",
        "size": "square_hd"
    },
    # Catalog 2 — Split S7: 7 double-spoke polished
    {
        "output_dir": CATALOG_DIR,
        "name": "wheel_02_split_s7",
        "prompt": NO_TEXT +
                  "luxury forged split-spoke wheel, 7 double Y-pattern spokes, "
                  "mirror polished silver aluminum with subtle chrome finish, "
                  "deep concave profile, 3/4 product view, "
                  "dramatic studio lighting, seamless black background, "
                  "hyperrealistic commercial photography, 8k",
        "size": "square_hd"
    },
    # Catalog 3 — Mesh Classic: 8-spoke matte black
    {
        "output_dir": CATALOG_DIR,
        "name": "wheel_03_mesh_classic",
        "prompt": NO_TEXT +
                  "luxury forged mesh wheel, 10-spoke intricate mesh pattern, "
                  "matte black finish with subtle graphite undertones, "
                  "slight concave profile, 3/4 product view, "
                  "soft studio lighting highlighting the mesh texture, "
                  "seamless black background, hyperrealistic photography, 8k",
        "size": "square_hd"
    }
]


def submit(prompt, size):
    data = json.dumps({
        "prompt": prompt,
        "image_size": size,
        "num_inference_steps": 4,
        "num_images": 1
    }).encode()
    req = urllib.request.Request(API_URL, data=data, headers={
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())['request_id']


def fetch(request_id, max_wait=60):
    url = f"https://queue.fal.run/fal-ai/flux/requests/{request_id}"
    for _ in range(max_wait):
        req = urllib.request.Request(url, headers={"Authorization": f"Key {FAL_KEY}"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            if 'images' in data:
                return data
        except urllib.error.HTTPError as e:
            if e.code not in (400, 404):
                raise
        time.sleep(1)
    raise TimeoutError()


def main():
    print(f"🎨 Генерация {len(WHEELS)} дисков (hero + каталог)\n")

    for i, w in enumerate(WHEELS, 1):
        print(f"[{i}/{len(WHEELS)}] {w['name']}")
        print(f"   ↳ Submitting to fal.ai...")
        rid = submit(w['prompt'], w['size'])
        print(f"   ↳ Waiting...")
        result = fetch(rid)
        img_url = result['images'][0]['url']

        # Скачивание jpg
        jpg_path = w['output_dir'] / f"{w['name']}.jpg"
        urllib.request.urlretrieve(img_url, jpg_path)
        print(f"   ↳ Downloaded ({result['timings']['inference']:.2f}s)")

        # Удаление фона
        print(f"   ↳ Removing background (rembg local)...")
        with open(jpg_path, 'rb') as f:
            png_data = remove(f.read())
        png_path = w['output_dir'] / f"{w['name']}_nobg.png"
        with open(png_path, 'wb') as f:
            f.write(png_data)
        print(f"   ✓ Saved: {png_path.name}\n")

    print(f"✅ Готово! Стоимость: ~${len(WHEELS) * 0.003:.3f}")


if __name__ == '__main__':
    main()
