#!/usr/bin/env python3
"""
Заготовка для работы с Replicate API (Flux, SAM для сегментации колёс, и т.д.)
Когда получишь API-ключ: export REPLICATE_API_TOKEN="r8_xxxxx"
"""
import os
import sys
import requests
import time
from pathlib import Path

API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
API_BASE = 'https://api.replicate.com/v1'

def check_token():
    if not API_TOKEN:
        print("⚠️  REPLICATE_API_TOKEN не установлен.")
        print("Получи ключ на https://replicate.com/account/api-tokens")
        print('Затем: export REPLICATE_API_TOKEN="r8_xxxxx"')
        sys.exit(1)

def run_model(model, version, input_data):
    """Запустить модель и дождаться результата."""
    check_token()

    headers = {
        'Authorization': f'Token {API_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Create prediction
    response = requests.post(
        f'{API_BASE}/predictions',
        headers=headers,
        json={'version': version, 'input': input_data}
    )
    prediction = response.json()

    if response.status_code != 201:
        print(f"Ошибка: {prediction}")
        return None

    # Poll for result
    prediction_url = prediction['urls']['get']
    print(f"Запущено: {prediction['id']}")

    while prediction['status'] not in ['succeeded', 'failed', 'canceled']:
        time.sleep(2)
        response = requests.get(prediction_url, headers=headers)
        prediction = response.json()
        print(f"  {prediction['status']}...")

    if prediction['status'] == 'succeeded':
        return prediction['output']
    else:
        print(f"Ошибка: {prediction.get('error', 'unknown')}")
        return None

# Примеры моделей (проверить актуальные версии на replicate.com):
# Flux Schnell — быстрая генерация изображений
FLUX_SCHNELL = 'black-forest-labs/flux-schnell'

# SAM — сегментация объектов (для поиска колёс на фото авто)
SAM = 'facebookresearch/sam:latest'

# RMBG — удаление фона
RMBG = 'briaai/bria-rmbg-2.0'

def generate_wheel_image(prompt):
    """Сгенерировать фото диска через Flux Schnell."""
    return run_model(FLUX_SCHNELL, 'latest', {
        'prompt': prompt,
        'num_outputs': 1,
        'aspect_ratio': '1:1',
        'output_format': 'png'
    })

if __name__ == '__main__':
    check_token()
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
        result = generate_wheel_image(prompt)
        print(f"Результат: {result}")
    else:
        print("Использование: python3 replicate_api.py 'prompt for image generation'")
