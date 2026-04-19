"""
Scrape 20 selected wheels from powerwheels.ru, remove background via fal.ai BiRefNet,
save to wheels/w1.png...w20.png, and update catalog.json (w21 Technic T17 preserved).
"""

import os
import re
import json
import time
import base64
import pathlib
import requests
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).parent.parent
load_dotenv(ROOT / ".env")
FAL_KEY = os.environ["FAL_KEY"]

# 20 curated wheels across 13 PowerWheels series (excluding Technic T17 which is already w21)
# Format: (id, slug, display_name, category, finish, sizes, pcd, et_range, price_from, price_to)
SELECTION = [
    ("w1",  "pw-5tech01",      "5Tech 01",        "monoblock",    "brushed silver",            ["19","20","21"],        ["5x112","5x120"],          "25-45", 640, 980),
    ("w2",  "pw-b07",          "Buggy B07",       "monoblock",    "matte black",               ["17","18","19"],        ["5x112","5x114.3"],        "15-35", 520, 780),
    ("w3",  "pw-carbon01",     "Carbon 01",       "multi-piece",  "carbon fiber gloss",        ["20","21","22"],        ["5x112","5x120","5x130"],  "20-40", 950,1450),
    ("w4",  "pw-c05",          "Casual C05",      "split-spoke",  "gloss black machined",      ["18","19","20"],        ["5x112","5x114.3"],        "30-45", 560, 820),
    ("w5",  "pw-c12",          "Casual C12",      "mesh",         "matte gunmetal",            ["19","20","21"],        ["5x112","5x120"],          "25-45", 580, 870),
    ("w6",  "pw-classic01",    "Classic 01",      "monoblock",    "polished silver",           ["18","19","20"],        ["5x112","5x114.3"],        "30-50", 490, 720),
    ("w7",  "pw-classic03",    "Classic 03",      "monoblock",    "matte bronze",              ["18","19","20"],        ["5x112","5x114.3","5x120"],"25-45", 510, 760),
    ("w8",  "pw-d01",          "Drag D01",        "monoblock",    "gloss black",               ["17","18","19","20"],   ["5x112","5x114.3"],        "20-40", 540, 820),
    ("w9",  "pw-dc05",         "Diamond Cut 05",  "concave",      "diamond cut silver",        ["19","20","21"],        ["5x112","5x120"],          "25-45", 620, 950),
    ("w10", "pw-dc015",        "Diamond Cut 015", "split-spoke",  "diamond cut black",         ["19","20","21","22"],   ["5x112","5x120","5x130"],  "20-40", 680,1050),
    ("w11", "pw-fl03",         "Floating FL03",   "concave",      "satin titanium",            ["19","20","21"],        ["5x112","5x120"],          "25-45", 660, 990),
    ("w12", "pw-fl07",         "Floating FL07",   "multi-piece",  "polished lip brushed face", ["20","21","22"],        ["5x112","5x120","5x130"],  "15-35", 780,1200),
    ("w13", "pw-l05",          "Luxury L05",      "multi-piece",  "high polish chrome",        ["19","20","21","22"],   ["5x112","5x120"],          "20-40", 820,1250),
    ("w14", "pw-l012-concave", "Luxury L012",     "concave",      "brushed champagne",         ["20","21","22"],        ["5x112","5x120","5x130"],  "20-40", 740,1100),
    ("w15", "pw-ms03",         "Motorsport MS03", "split-spoke",  "matte black machined",      ["18","19","20"],        ["5x112","5x114.3","5x120"],"25-45", 600, 920),
    ("w16", "pw-ms017",        "Motorsport MS17", "concave",      "gloss black",               ["19","20","21"],        ["5x112","5x120"],          "20-40", 640, 970),
    ("w17", "pw-offroad02",    "Offroad 02",      "monoblock",    "matte bronze",              ["17","18","20"],        ["5x150","6x139.7","5x127"],"0-25",  580, 880),
    ("w18", "pw-split02",      "Split 02",        "multi-piece",  "polished + black center",   ["19","20","21","22"],   ["5x112","5x120","5x130"],  "15-35", 780,1200),
    ("w19", "pw-split04",      "Split 04",        "multi-piece",  "brushed gold lip",          ["20","21","22"],        ["5x112","5x120"],          "20-40", 820,1280),
    ("w20", "pw-s01",          "Stratix S01",     "split-spoke",  "satin graphite",            ["19","20","21","22"],   ["5x112","5x114.3","5x120"],"20-45", 680,1050),
]

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def find_main_image(slug):
    """Fetch wheel page, return best quality image URL (1200x1200)."""
    r = requests.get(f"https://powerwheels.ru/wheel/{slug}/", headers=UA, timeout=30)
    r.raise_for_status()
    html = r.text
    # Prefer og:image
    m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if m:
        url = m.group(1)
        # Try to upgrade to 1200x1200
        url_1200 = re.sub(r'-\d+x\d+(\.\w+)$', r'-1200x1200\1', url)
        return url_1200
    # Fallback: first 1200x1200 in HTML
    m = re.search(r'(https://powerwheels\.ru/wp-content/uploads/[^"\s]*?-1200x1200\.(?:webp|png|jpg))', html)
    if m:
        return m.group(1)
    raise RuntimeError(f"No image found for {slug}")


def upload_to_fal(image_bytes, filename, content_type):
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    r = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers=headers,
        json={"content_type": content_type, "file_name": filename},
        timeout=30,
    )
    r.raise_for_status()
    d = r.json()
    requests.put(d["upload_url"], data=image_bytes, headers={"Content-Type": content_type}).raise_for_status()
    return d["file_url"]


def run_birefnet(image_url):
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    submit = requests.post(
        "https://queue.fal.run/fal-ai/birefnet",
        headers=headers,
        json={"image_url": image_url},
        timeout=30,
    )
    submit.raise_for_status()
    response_url = submit.json()["response_url"]
    for _ in range(30):
        time.sleep(2)
        r = requests.get(response_url, headers=headers, timeout=30)
        if r.status_code != 200:
            continue
        d = r.json()
        if d.get("status") in ("IN_QUEUE", "IN_PROGRESS"):
            continue
        return d["image"]["url"]
    raise RuntimeError("BiRefNet timeout")


def process_wheel(wid, slug):
    out_path = ROOT / "wheels" / f"{wid}.png"
    print(f"[{wid}] {slug}")
    # 1. Find image URL
    img_url = find_main_image(slug)
    print(f"  src: {img_url}")
    # 2. Download
    img_bytes = requests.get(img_url, headers=UA, timeout=30).content
    content_type = "image/webp" if img_url.endswith(".webp") else "image/jpeg" if img_url.endswith(".jpg") else "image/png"
    # 3. Upload to fal
    fal_url = upload_to_fal(img_bytes, f"{slug}.{content_type.split('/')[1]}", content_type)
    # 4. Run BiRefNet
    result_url = run_birefnet(fal_url)
    # 5. Download result
    result_bytes = requests.get(result_url, timeout=30).content
    out_path.write_bytes(result_bytes)
    print(f"  saved: {out_path.relative_to(ROOT)} ({len(result_bytes)//1024} KB)")


def main():
    # Process all 20 wheels
    for wid, slug, *_ in SELECTION:
        try:
            process_wheel(wid, slug)
        except Exception as e:
            print(f"  ERROR {wid}: {e}")
        time.sleep(1)

    # Build catalog.json — preserve w21 (Technic T17)
    catalog_path = ROOT / "wheels" / "catalog.json"
    old = json.loads(catalog_path.read_text())
    w21 = next((w for w in old if w["id"] == "w21"), None)

    new_catalog = []
    for wid, slug, name, cat, finish, sizes, pcd, et, pf, pt in SELECTION:
        new_catalog.append({
            "id": wid,
            "name": name,
            "category": cat,
            "finish": finish,
            "sizes": sizes,
            "pcd": pcd,
            "et_range": et,
            "price_from": pf,
            "price_to": pt,
            "image": f"wheels/{wid}.png",
            "source": f"https://powerwheels.ru/wheel/{slug}/",
        })
    if w21:
        new_catalog.append(w21)

    catalog_path.write_text(json.dumps(new_catalog, indent=2, ensure_ascii=False))
    print(f"\nCatalog written: {len(new_catalog)} wheels")


if __name__ == "__main__":
    main()
