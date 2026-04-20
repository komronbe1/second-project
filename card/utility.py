import re
from datetime import datetime, date
from django.core.exceptions import ValidationError


# =========================
# CARD EXPIRY PARSER
# =========================

PATTERN_MM_YY = re.compile(r"^(0[1-9]|1[0-2])[/\.](\d{2}|\d{4})$")
PATTERN_YYYY_MM = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def parse_expire(value):
    """
    Qabul qiladi:
    - 12/25
    - 12/2026
    - 2026-12
    """

    if not value:
        raise ValueError("Expire bo‘sh")

    raw = str(value).strip()

    # MM/YY yoki MM/YYYY
    match = PATTERN_MM_YY.match(raw)
    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if year < 100:
            year += 2000

        return datetime(year, month, 1)

    # YYYY-MM
    match = PATTERN_YYYY_MM.match(raw)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))

        return datetime(year, month, 1)

    raise ValueError(f"Noto‘g‘ri expire format: {value}")


# =========================
# LUHN CHECK
# =========================

def is_luhn_valid(card_number):
    card_number = str(card_number).replace(" ", "").replace("-", "")

    if not card_number.isdigit():
        return False

    digits = [int(d) for d in card_number]

    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        if doubled > 9:
            doubled -= 9
        digits[i] = doubled

    return sum(digits) % 10 == 0


# =========================
# PHONE VALIDATOR
# =========================

def validate_phone(value):
    clean_phone = re.sub(r"\D", "", str(value))

    if not re.match(r"^(998)?\d{9}$", clean_phone):
        raise ValidationError("Telefon noto‘g‘ri (998901234567)")

    return clean_phone


# =========================
# EXPIRE CHECK
# =========================

def is_expired(expire_date):
    if not expire_date:
        return False

    today = date.today().replace(day=1)
    return expire_date < today


# =========================
# MASK CARD
# =========================

def card_mask(card_number):
    card_number = str(card_number)
    return f"{card_number[:4]} **** **** {card_number[-4:]}"


# =========================
# MASK PHONE
# =========================

def phone_mask(phone: str) -> str:
    phone = str(phone).replace("+", "").replace(" ", "")

    if len(phone) == 12 and phone.startswith("998"):
        return f"+{phone[:3]} {phone[3]}** *** ** {phone[-2:]}"

    if len(phone) == 9:
        return f"+998 {phone[0]}** *** ** {phone[-2:]}"

    return phone