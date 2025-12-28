from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import StateFilter
import config
import keyboards

# Чтобы не было циклических импортов, функции меню импортируем внутри, 
# либо используем router.message внутри menu.py для перехвата.
# Но здесь мы используем подход с проверкой текста.

router = Router()

class Calculator(StatesGroup):
    waiting_for_amount = State()

# 1. Вход в калькулятор
@router.message(F.text == "💱 Курс валют", StateFilter("*"))
async def start_calc(message: types.Message, state: FSMContext):
    await state.clear()
    
    rates = config.get_rates()
    rub_d = "{:,.0f}".format(rates['rub_rate']).replace(',', '.')
    usdt_d = "{:,.0f}".format(rates['usdt_rate']).replace(',', '.')
    usd_d = "{:,.0f}".format(rates['usd_rate']).replace(',', '.')

    text = (
        "💱 <b>КУРС ВАЛЮТ НА СЕГОДНЯ:</b>\n\n"
        f"🇷🇺 10.000 ₽ ➔ {rub_d} ₫\n"
        f"💎 100 USDT ➔ {usdt_d} ₫\n"
        f"💵 100 USD ➔ {usd_d} ₫\n\n"
        "👇 <b>Что будем менять?</b>"
    )
    await message.answer(text, reply_markup=keyboards.get_calc_keyboard())

# 2. Выбор валюты
@router.callback_query(F.data.startswith("calc_"))
async def ask_amount(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    await state.update_data(selected_currency=currency)
    await state.set_state(Calculator.waiting_for_amount)
    
    currency_names = {"rub": "RUB", "usdt": "USDT", "usd": "USD"}
    name = currency_names.get(currency, "валюту")
    
    await callback.message.answer(f"👇 Введите сумму в <b>{name}</b> (только цифры):")
    await callback.answer()

# 3. Расчет (Обработка ввода)
@router.message(Calculator.waiting_for_amount)
async def process_calc(message: types.Message, state: FSMContext):
    # ПРОВЕРКА НА КНОПКИ МЕНЮ (чтобы не застрять)
    # Важно: тут мы не можем вызвать функции из menu.py напрямую, чтобы не было кругового импорта.
    # Поэтому мы просто сбрасываем стейт, если текст похож на кнопку.
    menu_buttons = ["🛵 Аренда байков", "🚘 Трансфер", "🇻🇳 Визаран", "📞 Контакты", "💱 Курс валют"]
    if message.text in menu_buttons:
        await state.clear()
        # Aiogram сам перенаправит сообщение в нужный хендлер menu.py, так как стейт очищен
        # Для этого нам нужно "пробросить" сообщение дальше. 
        # Но проще всего просто сказать "вышли". 
        # Однако, благодаря магическому фильтру StateFilter("*") в menu.py, те хендлеры сработают сами!
        # Так что здесь нам достаточно просто проверить и если это кнопка - ничего не делать (пусть другой хендлер ловит)
        # НО! Этот хендлер ловит состояние.
        
        # ЛУЧШИЙ ВАРИАНТ: 
        # Просто выходим. А сообщение обработается хендлерами из menu.py, потому что они имеют StateFilter('*')
        return 

    # Логика калькулятора
    clean_text = message.text.replace(" ", "").replace(".", "").replace(",", "")
    if not clean_text.isdigit():
        await message.answer("⚠️ Введите только цифры.")
        return
    
    amount_input = int(clean_text)
    data = await state.get_data()
    currency = data.get("selected_currency", "rub")
    
    rates = config.get_rates()
    
    if currency == "rub":
        rate = rates['rub_rate']
        amount_vnd = (amount_input * rate) / 10000
        input_label = "RUB"
        info = "Принимаем: Сбер, СБП."
    else:
        rate = rates['usdt_rate'] if currency == "usdt" else rates['usd_rate']
        amount_vnd = (amount_input * rate) / 100
        input_label = currency.upper()
        info = "Выдаем наличные VND."

    vnd_fmt = "{:,.0f}".format(amount_vnd).replace(',', '.')
    input_fmt = "{:,.0f}".format(amount_input).replace(',', '.')
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Забронировать обмен", callback_data="book_exchange")
    
    await message.answer(
        f"💰 <b>Расчет:</b>\n{input_fmt} {input_label} = <b>{vnd_fmt} VND</b>\n\n{info}",
        reply_markup=builder.as_markup()
    )