#!/usr/bin/env python3
"""
Пакетная обработка фото дисков для каталога:
- удаление фона
- ресайз до стандартного размера
- оптимизация веса
"""
import sys
from pathlib import Path
from PIL import Image
from rembg import remove, new_session

WHEELS_DIR = Path(__file__).parent.parent / 'wheels'
TARGET_SIZE = 800  # pixels

def process_wheel(input_path, output_path=None):
    if output_path is None:
        output_path = input_path.with_stem(input_path.stem + '_processed')

    # Удалить фон
    session = new_session('isnet-general-use')
    with open(input_path, 'rb') as f:
        data = f.read()
    no_bg_data = remove(data, session=session)

    # Открыть и обработать
    from io import BytesIO
    img = Image.open(BytesIO(no_bg_data))

    # Ресайз с сохранением пропорций
    img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

    # Квадратный canvas с прозрачностью
    canvas = Image.new('RGBA', (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))
    offset = ((TARGET_SIZE - img.size[0]) // 2, (TARGET_SIZE - img.size[1]) // 2)
    canvas.paste(img, offset, img if img.mode == 'RGBA' else None)

    canvas.save(output_path, 'PNG', optimize=True)
    print(f"✓ {input_path.name} → {output_path.name}")
    return output_path

if __name__ == '__main__':
    if len(sys.argv) > 1:
        process_wheel(Path(sys.argv[1]))
    else:
        # Обработать все диски в папке wheels/
        for wheel in sorted(WHEELS_DIR.glob('*.png')):
            if '_processed' not in wheel.name:
                process_wheel(wheel)
