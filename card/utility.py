
from email import parser
import re
from django.core.exceptions import ValidationError
from datetime import datetime, date

from dateutil import parser # pip install python-dateutil

def parse_expire(value):
    try:
        # Deyarli har qanday sana formatini tushunadi
        dt = parser.parse(str(value))
        return dt
    except:
        raise ValueError("Format xato")

def is_luhn_valid(card_number):
    """
    Karta raqami Luhn algoritmi bo'yicha to'g'riligini tekshiradi.
    """
    # Karta raqamidan faqat raqamlarni olib qolamiz
    card_number = str(card_number).replace(" ", "").replace("-", "")
    
    if not card_number.isdigit():
        return False

    digits = [int(d) for d in card_number]
    
    # 1. O'ngdan chapga qarab, har ikkinchi raqamni 2 ga ko'paytiramiz
    for i in range(len(digits) - 2, -1, -2):
        multiplied = digits[i] * 2
        # 2. Agar ko'paytma 9 dan katta bo'lsa, uning raqamlari yig'indisini olamiz
        # (yoki shunchaki 9 ni ayirib tashlaymiz - natija bir xil bo'ladi)
        if multiplied > 9:
            multiplied -= 9
        digits[i] = multiplied
        
    # 3. Barcha raqamlar yig'indisi 10 ga qoldiqsiz bo'linishi kerak
    return sum(digits) % 10 == 0


def validate_phone(value):
    # Faqat raqamlarni qoldiramiz
    clean_phone = re.sub(r'\D', '', value)
    
    # O'zbekiston raqami formati: 998901234567 yoki 901234567
    if not re.match(r'^(998)?\d{9}$', clean_phone):
        raise ValidationError("Telefon raqami formati noto'g'ri!")
    return clean_phone


def is_expired(expire_date):
    if not expire_date:
        return False
    today = date.today().replace(day=1)
    return expire_date < today



def normalize_card(value):
    return re.sub(r'\D', '', value or '')


from datetime import datetime

# MM/YY yoki MM/YYYY
PATTERN_MM_YY = re.compile(r"^(0[1-9]|1[0-2])[/\.](\d{2}|\d{4})$")

# YYYY-MM
PATTERN_YYYY_MM = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
def parse_expire(value):
    if not value:
        raise ValueError("Expire bo‘sh")

    raw = str(value).strip()

    # 🔹 1. MM/YY yoki MM/YYYY (04/25, 11.2026)
    match = PATTERN_MM_YY.match(raw)
    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if year < 100:
            year += 2000

        return datetime(year, month, 1)

    # 🔹 2. YYYY-MM (2025-07)
    match = PATTERN_YYYY_MM.match(raw)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))

        return datetime(year, month, 1)

    raise ValueError(f"Noto‘g‘ri format: {value}")



def card_mask(card_number):
    card_number = str(card_number)
    card = f"{card_number[:4]} **** **** {card_number[-4:]}"
    return card


def phone_mask(phone: str) -> str:
    phone = str(phone).replace("+", "").replace(" ", "")

    # +998901234567 (12 ta raqam)
    if len(phone) == 12 and phone.startswith("998"):
        return f"+{phone[:3]} {phone[3]}** *** ** {phone[-2:]}"

    # 901234567 (9 ta raqam)
    if len(phone) == 9:
        return f"+998 {phone[0]}** *** ** {phone[-2:]}"

    raise ValueError("Invalid phone number format")
