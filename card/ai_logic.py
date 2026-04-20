import google.generativeai as genai
import json
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


def clean_data_with_ai(raw_csv_data: str) -> list | None:
    prompt = f"""
Ты — эксперт по очистке банковских данных. 
Вот сырые данные из Excel таблицы с банковскими картами:

{raw_csv_data}

Твоя задача — нормализовать КАЖДУЮ строку и вернуть результат СТРОГО в формате JSON массива.

ПРАВИЛА ОЧИСТКИ:

1. card_number:
   - Убери все пробелы и тире
   - Оставь только 16 цифр
   - Пример: "8600 1234 5678 9012" → "8600123456789012"

2. expire:
   - Приведи к формату MM/YY
   - "2024-12" → "12/24"
   - "12.2024" → "12/24"
   - "12/2024" → "12/24"
   - "12.24"   → "12/24"

3. phone:
   - Убери все символы кроме цифр
   - Если 9 цифр — добавь префикс 998
   - Если пусто или None — оставь пустую строку ""
   - Пример: "97 303 03 03" → "998973030303"
   - Пример: "973-03-03"    → "998973030303" (9 цифр → добавь 998)

4. status:
   - Только одно из: "active", "inactive", "expired"
   - Если непонятно — ставь "inactive"

5. balance:
   - Только число с двумя знаками после запятой
   - Убери запятые-разделители тысяч
   - Пример: "842,714,800.00" → 842714800.00
   - Пример: "22 300"         → 22300.00

ФОРМАТ ОТВЕТА (только JSON, без пояснений):
[
  {{
    "card_number": "8600123456789012",
    "expire": "12/24",
    "phone": "998973030303",
    "status": "active",
    "balance": 5000.00
  }}
]
"""

    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        clean_json = json.loads(response.text)
        print("====== ОТВЕТ ОТ AI ======")
        print(json.dumps(clean_json, indent=4, ensure_ascii=False))
        print(f"✅ AI очистил {len(clean_json)} записей")
        print("=========================")
        return clean_json
    except json.JSONDecodeError:
        print("❌ Ошибка: AI вернул не JSON!")
        print(response.text)
        return None