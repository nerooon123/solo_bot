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

    # Расчёт HP и MP с учётом силы и интеллекта
    strength = user[2]
    intelligence = user[6]
    base_hp = 100
    base_mp = 100
    hp = int(base_hp * (1 + strength * 0.100))
    mp = int(base_mp * (1 + intelligence * 0.100))

    greeting = (
        f"🏰 Профиль игрока\n"
        f"Имя: {username}\n"
        f"Титул: {user[11]}\n"
        f"Профессия: {user[12]}\n"
        f"Уровень: {user[13]}\n"
        f"XP: {user[14]}/100\n"
        f"HP: {hp}\n"
        f"MP: {mp}\n"
        f"\n"
        f"Характеристики:\n"
        f"— 🪓 Сила: {strength}\n"
        f"— 🤸 Ловкость: {user[3]}\n"
        f"— 🛡️ Выносливость: {user[4]}\n"
        f"— 👁️ Восприятие: {user[5]}\n"
        f"— 📚 Интеллект: {intelligence}\n"
        f"— 🎭 Харизма: {user[7]}\n"
        f"— 🔥 Сила Воли: {user[8]}\n\n"
        f"Нажми кнопки ниже, чтобы изучить свои навыки и характеристики."
    )

    await message.answer(greeting, reply_markup=get_profile_keyboard(), parse_mode="Markdown")
