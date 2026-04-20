import re
import requests
from datetime import date

BOT_TOKEN = "8568777588:AAFKl0C2y-lux54xLInATa9Jb-dx4K_1v6s"
ADMIN_CHAT_ID = "-5243783628"


def format_card(raw_card: str) -> str:
    """Убирает пробелы/тире, оставляет 16 цифр"""
    return "".join(re.findall(r'\d+', str(raw_card)))


def format_phone(raw_phone: str) -> str:
    """Нормализует телефон → 998XXXXXXXXX"""
    if not raw_phone:
        return ""
    clean = "".join(re.findall(r'\d+', str(raw_phone)))
    if len(clean) == 9:
        clean = '998' + clean
    return clean if len(clean) == 12 else ""


def card_mask(card_number: str) -> str:
    """8600 **** **** 9012"""
    c = format_card(card_number)
    if len(c) != 16:
        return card_number
    return f"{c[:4]} **** **** {c[12:]}"


def phone_mask(phone: str) -> str:
    """998 (90) 123-45-67"""
    c = format_phone(str(phone))
    if len(c) != 12:
        return phone or "—"
    return f"{c[:3]} ({c[3:5]}) {c[5:8]}-{c[8:10]}-{c[10:]}"


def format_expire(raw: str) -> date | None:
    """Парсит разные форматы даты → date(YYYY, MM, 1) или None"""
    raw = str(raw).strip()
    patterns = [
        (r'^(\d{2})/(\d{2})$',   lambda m: date(2000 + int(m.group(2)), int(m.group(1)), 1)),
        (r'^(\d{2})\.(\d{4})$',  lambda m: date(int(m.group(2)), int(m.group(1)), 1)),
        (r'^(\d{4})-(\d{2})$',   lambda m: date(int(m.group(1)), int(m.group(2)), 1)),
        (r'^(\d{2})\.(\d{2})$',  lambda m: date(2000 + int(m.group(2)), int(m.group(1)), 1)),
        (r'^(\d{2})/(\d{4})$',   lambda m: date(int(m.group(2)), int(m.group(1)), 1)),
        (r'^(\d{2})-(\d{4})$',   lambda m: date(int(m.group(2)), int(m.group(1)), 1)),
    ]
    for pattern, parser in patterns:
        m = re.match(pattern, raw)
        if m:
            try:
                return parser(m)
            except ValueError:
                return None
    return None


def prepare_message(card_number: str, balance, lang="UZ") -> str:
    """Формирует текст сообщения для карты"""
    masked = card_mask(card_number)
    if lang == "UZ":
        return (
            f"Sizning kartangiz {masked} aktiv va "
            f"foydalanishga {balance:,.2f} UZS mavjud!"
        )
    return f"Your card {masked} is active. Balance: {balance:,.2f} UZS"


def send_message(message: str, chat_id: str = ADMIN_CHAT_ID) -> bool:
    """Отправляет сообщение через Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": message})
        if response.status_code == 200:
            print(f"✅ Отправлено в Telegram (chat_id={chat_id})")
            return True
        print(f"❌ Telegram error: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Сеть: {e}")
        return False


def send_admin_notification(count: int, method: str = "Обычный") -> bool:
    text = (
        f"📊 Отчет об импорте\n\n"
        f"Метод: {method}\n"
        f"Успешно добавлено карт: {count}\n"
        f"Статус: Завершено ✅"
    )
    return send_message(text, ADMIN_CHAT_ID)