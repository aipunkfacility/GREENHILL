from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import config
import keyboards

router = Router()

class AdminStates(StatesGroup):
    waiting_for_new_rate = State()

@router.message(Command("admin"))
async def open_admin_panel(message: types.Message):
    allowed_admins = config.get_admins()
    if message.from_user.id not in allowed_admins:
        return 
    await message.answer(
        f"⚙️ <b>Админ-панель</b>\n"
        f"Текущий курс: 1 RUB = <b>{config.RUB_TO_VND_RATE} VND</b>",
        reply_markup=keyboards.get_admin_keyboard()
    )

@router.callback_query(F.data == "admin_change_rate")
async def admin_ask_rate(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый курс (число):")
    await state.set_state(AdminStates.waiting_for_new_rate)
    await callback.answer()

@router.message(AdminStates.waiting_for_new_rate)
async def admin_save_rate(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Это не число.")
        return
    new_rate = int(message.text)
    config.RUB_TO_VND_RATE = new_rate
    await message.answer(f"✅ Курс обновлен: {new_rate} VND")
    await state.clear()

@router.callback_query(F.data == "admin_close")
async def admin_close(callback: types.CallbackQuery):
    await callback.message.delete()