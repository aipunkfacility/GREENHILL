from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import LinkPreviewOptions # <--- Добавили импорт для настройки превью
import config
import keyboards
import logging

router = Router()

# СТАРТ
@router.message(CommandStart(), StateFilter("*"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Xin chào, {message.from_user.first_name}! 🇻🇳\n"
        f"Добро пожаловать в <b>Green Hill Tours</b>.",
        reply_markup=keyboards.get_main_menu()
    )

# --- 🛵 ГЛАВНОЕ МЕНЮ БАЙКОВ ---
@router.message(F.text == "🛵 Аренда байков", StateFilter("*"))
async def bike_catalog(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите категорию транспорта:", reply_markup=keyboards.get_bike_catalog_keyboard())

# --- ПОКАЗ КАТЕГОРИЙ (ГАЛЕРЕЯ) ---
@router.callback_query(F.data.startswith("bike_"))
async def show_bike_category(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    
    bikes_list = []

    if category == "scooters":
        bikes_list = [
            ("Honda Vision", "Легкий, экономичный. Идеал для новичков.\n💰 150к/день", "IMG_VISION"),
            ("Honda Lead", "Огромный багажник! Лучший выбор для покупок.\n💰 150к/день", "IMG_LEAD"),
            ("Honda Airblade", "Мощный, стильный, устойчивый.\n💰 150к/день", "IMG_AIRBLADE")
        ]
    
    elif category == "maxi":
        bikes_list = [
            ("Honda PCX 160 (ABS)", "Топ комфорт, ABS, бесключевой доступ.\n💰 200к/день", "IMG_PCX160"),
            ("Honda PCX 150", "Бизнес-класс. Проверенная классика.\n💰 200к/день", "IMG_PCX150"),
            ("Yamaha NVX 155 (Black)", "Черный матовый. Мощь и стиль.\n💰 200к/день", "IMG_NVX_B"),
            ("Yamaha NVX 155 (Red)", "Яркий красный. Спорт-режим.\n💰 200к/день", "IMG_NVX_R")
        ]
        
    elif category == "moto":
        bikes_list = [
            ("Suzuki GSX 150", "Механика для драйва и серпантинов.\n💰 300к/день", "IMG_SUZUKI")
        ]

    await callback.answer()

    if not bikes_list:
        await callback.message.answer("В этой категории пока нет фото.")
        return

    for name, desc, img_var_name in bikes_list:
        photo_id = getattr(config, img_var_name, None)
        
        builder = InlineKeyboardBuilder()
        builder.button(text=f"✅ Забронировать {name}", callback_data=f"book_{category}")
        
        caption = f"🛵 <b>{name}</b>\n{desc}"
        
        if photo_id:
            try:
                await callback.message.answer_photo(photo=photo_id, caption=caption, reply_markup=builder.as_markup())
            except Exception as e:
                logging.error(f"Ошибка с фото {name} ({img_var_name}): {e}")
                await callback.message.answer(caption, reply_markup=builder.as_markup())
        else:
            await callback.message.answer(caption, reply_markup=builder.as_markup())

# --- ВИЗАРАН ---
@router.message(F.text == "🇻🇳 Визаран", StateFilter("*"))
async def show_visarun(message: types.Message, state: FSMContext):
    await state.clear()
    kb = keyboards.get_booking_keyboard("visarun")
    if getattr(config, 'IMG_VISARUN', None):
        await message.answer_photo(photo=config.IMG_VISARUN, caption=config.VISARUN_INFO, reply_markup=kb)
    else:
        # Тут тоже отключаем превью на всякий случай
        await message.answer(
            config.VISARUN_INFO, 
            reply_markup=kb, 
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )

# --- ТРАНСФЕР ---
@router.message(F.text == "🚘 Трансфер", StateFilter("*"))
async def show_transfer(message: types.Message, state: FSMContext):
    await state.clear()
    kb = keyboards.get_booking_keyboard("transfer")
    if getattr(config, 'IMG_TRANSFER', None):
        await message.answer_photo(photo=config.IMG_TRANSFER, caption=config.TRANSFER_INFO, reply_markup=kb)
    else:
        await message.answer(
            config.TRANSFER_INFO, 
            reply_markup=kb,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )

# --- КОНТАКТЫ (ЗДЕСЬ БЫЛ WHATSAPP) ---
@router.message(F.text == "📞 Контакты", StateFilter("*"))
async def show_contacts(message: types.Message, state: FSMContext):
    await state.clear()
    # [FIX] Добавил link_preview_options(is_disabled=True)
    await message.answer(
        config.CONTACT_INFO, 
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )

# --- ОБРАБОТЧИК ЗАЯВОК ---
@router.callback_query(F.data.startswith("book_"))
async def process_booking(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    category_code = parts[1]
    
    user = callback.from_user
    service_names = { 
        "scooters": "🛵 Скутер", 
        "maxi": "🏍 Макси-скутер", 
        "moto": "🏎 Мотоцикл", 
        "visarun": "🚐 ВИЗАРАН", 
        "transfer": "🚘 ТРАНСФЕР", 
        "exchange": "💱 ОБМЕН" 
    }
    service_name = service_names.get(category_code, category_code.upper())
    
    try:
        model_hint = callback.message.caption.split("\n")[0]
    except:
        model_hint = ""

    admin_text = (
        f"🔥 <b>НОВАЯ ЗАЯВКА!</b>\n"
        f"👤: <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
        f"🛒 Категория: <b>{service_name}</b>\n"
        f"📝 Инфо: {model_hint}"
    )
    
    admins = config.get_admins()
    for admin_id in admins:
        try:
            await callback.bot.send_message(chat_id=admin_id, text=admin_text)
        except Exception as e:
            logging.error(f"Error sending to admin {admin_id}: {e}")
            
    await callback.message.answer("✅ <b>Заявка принята!</b> Менеджер скоро напишет вам.")
    await callback.answer()