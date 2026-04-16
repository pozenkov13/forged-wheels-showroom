#!/usr/bin/env python3
"""
Удаление фона с фото автомобиля через rembg (бесплатно, локально).
Использование: python3 remove_bg.py input.jpg [output.png]
"""
import sys
from pathlib import Path
from rembg import remove, new_session
from PIL import Image

def remove_background(input_path, output_path=None, model='u2net'):
    """
    Удаляет фон с изображения.

    model: 'u2net' (общий), 'isnet-general-use' (лучше для машин),
           'silueta' (быстрый, хуже качество)
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix('.png').with_stem(input_path.stem + '_nobg')

    session = new_session(model)

    print(f"Обрабатываю: {input_path}")
    with open(input_path, 'rb') as f:
        input_data = f.read()

    output_data = remove(input_data, session=session)

    with open(output_path, 'wb') as f:
        f.write(output_data)

    img = Image.open(output_path)
    print(f"Готово: {output_path} ({img.size[0]}x{img.size[1]})")
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python3 remove_bg.py input.jpg [output.png] [model]")
        print("Модели: u2net (по умолчанию), isnet-general-use, silueta")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    model = sys.argv[3] if len(sys.argv) > 3 else 'isnet-general-use'

    remove_background(input_file, output_file, model)
