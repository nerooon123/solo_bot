from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from database import add_user, get_user_profile
from keyboards.profile import get_profile_keyboard

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Безымянный Герой"

    add_user(user_id, username)
    user = get_user_profile(user_id)

    greeting = (
        f"🏰 Добро пожаловать, *{username}*, в хроники Реального Мира!\n\n"
        f"Ты пробуждаешься в мире, где каждая черта личности — это навык, "
        f"каждое действие — квест, а прокачка происходит не в подземельях, а в повседневности.\n\n"
        f"🧾 Вот твой начальный профиль:\n"
        f"— 🪓 Сила: {user[2]}\n"
        f"— 🤸 Ловкость: {user[3]}\n"
        f"— 🛡️ Выносливость: {user[4]}\n"
        f"— 👁️ Восприятие: {user[5]}\n"
        f"— 📚 Интеллект: {user[6]}\n"
        f"— 🎭 Харизма: {user[7]}\n"
        f"— 🔥 Сила Воли: {user[8]}\n\n"
        f"Нажми кнопки ниже, чтобы изучить свои навыки и характеристики."
    )

    await message.answer(greeting, reply_markup=get_profile_keyboard(), parse_mode="Markdown")
