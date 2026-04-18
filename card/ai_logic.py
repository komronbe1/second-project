import google.generativeai as genai
import json
import os
from django.conf import settings

# Настройка API ключа (лучше хранить его в .env или settings)
genai.configure(api_key=settings.GEMINI_API_KEY)

def clean_data_with_ai(raw_csv_data):
    prompt = f"""
    Ты — эксперт по очистке данных. Вот сырые данные из банковской таблицы (CSV).
    Твоя задача: нормализовать их и вернуть СТРОГО в формате JSON.
    ... (твой промпт) ...
    """

    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    # Рекомендую добавить параметр response_mime_type, чтобы Gemini всегда отдавал чистый JSON
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        clean_json = json.loads(response.text)
        print("====== ОТВЕТ ОТ AI ======")
        print(json.dumps(clean_json, indent=4, ensure_ascii=False)) # Красиво выведет JSON
        print("=========================")
        return clean_json
    except json.JSONDecodeError:
        print("Ошибка: AI вернул не JSON!", response.text)
        return None