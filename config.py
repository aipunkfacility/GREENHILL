import os
import json
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")

# --- [FIX] НАСТРОЙКА ПУТЕЙ ДЛЯ AMVERA ---
# Проверяем, есть ли папка /data (она есть только на сервере)
if os.path.exists("/data"):
    DATA_DIR = "/data"
else:
    DATA_DIR = "."  # Если мы на компе, сохраняем рядом

# Теперь файлы будут лежать в правильном месте (в вечном хранилище)
ADMINS_FILE = os.path.join(DATA_DIR, "admins.json")
RATES_FILE = os.path.join(DATA_DIR, "rates.json")

# --- РАБОТА С АДМИНАМИ ---
def get_admins():
    # Если файла нет, создаем его и добавляем админа из .env
    if not os.path.exists(ADMINS_FILE):
        env_admin = os.getenv("ADMIN_ID")
        # Если в .env есть ID, добавляем его в список, иначе пустой список
        initial_admins = [int(env_admin)] if env_admin else []
        
        with open(ADMINS_FILE, 'w') as f:
            json.dump(initial_admins, f)
        return initial_admins

    try:
        with open(ADMINS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def add_admin_id(new_id: int):
    admins = get_admins()
    if new_id not in admins:
        admins.append(new_id)
        with open(ADMINS_FILE, 'w') as f:
            json.dump(admins, f)

def remove_admin_id(target_id: int):
    admins = get_admins()
    if target_id in admins:
        admins.remove(target_id)
        with open(ADMINS_FILE, 'w') as f:
            json.dump(admins, f)

# --- РАБОТА С КУРСАМИ ---
def get_rates():
    """Читает курсы из файла"""
    try:
        with open(RATES_FILE, 'r') as f:
            return json.load(f)
    except:
        # Дефолтные значения, если файла еще нет
        return {
            "rub_rate": 3090000,
            "usdt_rate": 2600000,
            "usd_rate": 2610000,
            "eur_rate": 2850000,
            "cny_rate": 36000
        }

def update_rates(rub, usdt, usd, eur, cny):
    """Обновляет курсы"""
    data = {
        "rub_rate": rub,
        "usdt_rate": usdt,
        "usd_rate": usd,
        "eur_rate": eur,
        "cny_rate": cny
    }
    with open(RATES_FILE, 'w') as f:
        json.dump(data, f)

# Переменная для совместимости (чтобы main.py не падал при старте)
RUB_TO_VND_RATE = get_rates()['rub_rate']

# ==========================================
# 🖼 ID КАРТИНОК (Добавлено ?v=1 для сброса кэша Telegram)
# ==========================================
IMG_VISION = "https://greenhill-admin.duckdns.org/images/vision.jpg?v=1"
IMG_LEAD = "https://greenhill-admin.duckdns.org/images/lead.jpg?v=1"
IMG_AIRBLADE = "https://greenhill-admin.duckdns.org/images/airblade.jpg?v=1"

IMG_PCX160 = "https://greenhill-admin.duckdns.org/images/pcx160.jpg?v=1"
IMG_PCX150 = "https://greenhill-admin.duckdns.org/images/pcx150.jpg?v=1"
IMG_NVX_B = "https://greenhill-admin.duckdns.org/images/nvx_b.jpg?v=1"
IMG_NVX_R = "https://greenhill-admin.duckdns.org/images/nvx_r.jpg?v=1"

IMG_SUZUKI = "https://greenhill-admin.duckdns.org/images/suzuki.jpg?v=1"

IMG_TRANSFER = "https://greenhill-admin.duckdns.org/images/transfer.jpg?v=1"
IMG_VISARUN = "https://greenhill-admin.duckdns.org/images/visarun.jpg?v=1"
IMG_EXCHANGE = "https://greenhill-admin.duckdns.org/images/exchange.jpg?v=1"

# ==========================================
# 📝 ТЕКСТЫ СООБЩЕНИЙ
# ==========================================

TRANSFER_INFO = """
🚘 <b>Трансфер Аэропорт ⇄ Муйне</b>

Забудьте про тесные автобусы и долгое ожидание такси. Начните отдых с комфорта.

<b>Автомобиль:</b> Toyota Fortuner (7 мест).
Просторный салон, мощный кондиционер, огромный багажник (влезают чемоданы и кайт-снаряжение).

🛣 <b>Маршрут:</b>
Едем по <b>новой скоростной трассе</b>. Время в пути сократилось! Водители опытные, стиль вождения — спокойный и безопасный.

<b>Направления:</b>
• Аэропорт Хошимин (SGN)
• Нячанг / Камрань
• Далат / Вунгтау

🏷 <b>Цена:</b> Фиксированная. Никаких доплат в пути.
"""

VISARUN_INFO = """
🚐 <b>Визаран в Камбоджу: «Под ключ» и с комфортом</b>

Подходит срок визы? Организуем продление одним днем. Вам не нужно разбираться с бумагами и искать транспорт — мы всё берем на себя.

✅ <b>Что включено в стоимость:</b>
• Трансфер туда-обратно (комфортабельный микроавтобус).
• Оформление Е-визы во Вьетнам.
• Оформление Е-визы в Камбоджу.

🕓 <b>Тайминг:</b>
• Выезд ночью: 02:30 (чтобы пройти границу первыми).
• Возвращение в Муйне: 16:00 – 17:00 (успеваете на закат).

💰 <b>Стоимость:</b> 4 200 000 VND (Всё включено).

Для бронирования нужно фото паспорта и дата окончания текущей визы.
"""

CONTACT_INFO = """
📞 <b>Наши контакты:</b>

📩 Бронь и вопросы: @GreenHill_Support
💬 WhatsApp: <a href="https://wa.me/84372733431">Написать</a>
📢 Наш канал: @GreenHill_tours

📍 <b>Наши офисы в Муйне:</b>

🏢 <b>Офис 1 (Green Hill Resort & Spa)</b>
👉 <a href="https://maps.app.goo.gl/CoBgDGcdES5Ktx1G6">121 Nguyễn Đình Chiểu</a>

🏢 <b>Офис 2</b>
👉 <a href="https://maps.app.goo.gl/yUP4APRYq7dLKTDn9">107 Nguyễn Đình Chiểu</a>
"""