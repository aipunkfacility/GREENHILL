from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu():
    """Главная клавиатура (внизу экрана)"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="💱 Курс валют")
    builder.button(text="🛵 Аренда байков")
    builder.button(text="🚘 Трансфер")
    builder.button(text="🇻🇳 Визаран")
    builder.button(text="📞 Контакты")
    builder.adjust(2)  # 2 кнопки в ряд
    return builder.as_markup(resize_keyboard=True)


def get_calc_keyboard():
    """Кнопки выбора валюты в калькуляторе"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Рубли (RUB)", callback_data="calc_rub")
    builder.button(text="💎 Крипта (USDT)", callback_data="calc_usdt")
    builder.button(text="💵 Доллары (USD)", callback_data="calc_usd")
    builder.button(text="🇪🇺 Евро (EUR)", callback_data="calc_eur")
    builder.button(text="🇨🇳 Юани (CNY)", callback_data="calc_cny")
    builder.adjust(1)
    return builder.as_markup()



def get_bike_catalog_keyboard():
    """Меню категорий байков"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🛵 Скутеры", callback_data="bike_scooters")
    builder.button(text="🏍 Макси", callback_data="bike_maxi")
    builder.button(text="🏎 Мото", callback_data="bike_moto")
    builder.adjust(1)
    return builder.as_markup()


def get_booking_keyboard(category_code):
    """Кнопка бронирования под услугой"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Забронировать", callback_data=f"book_{category_code}")
    return builder.as_markup()
