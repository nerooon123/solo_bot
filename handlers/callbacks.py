from aiogram import Router
from aiogram.types import CallbackQuery
from database import get_user_profile, add_user
from keyboards.profile import get_back_keyboard, get_profile_keyboard, get_stats_keyboard
import sqlite3
import json
import random

router = Router()

@router.callback_query(lambda c: c.data == "skills")
async def skills_callback(callback: CallbackQuery):
    user = get_user_profile(callback.from_user.id)
    skills_raw = user[9]
    skills = json.loads(skills_raw) if skills_raw else {}
    text = "📘 Твои навыки:\n" + "\n".join(
        [f"— {name}: {level} ур." for name, level in skills.items()]
    ) if skills else "📜 У тебя пока нет изученных навыков."

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())

@router.callback_query(lambda c: c.data == "stats")
async def stats_callback(callback: CallbackQuery):
    user = get_user_profile(callback.from_user.id)
    text = (
        f"🧬 Характеристики (Свободных очков: {user[10]}):\n"
        f"— 🪓 Сила: {user[2]}\n"
        f"— 🤸 Ловкость: {user[3]}\n"
        f"— 🛡️ Выносливость: {user[4]}\n"
        f"— 👁️ Восприятие: {user[5]}\n"
        f"— 📚 Интеллект: {user[6]}\n"
        f"— 🎭 Харизма: {user[7]}\n"
        f"— 🔥 Сила Воли: {user[8]}"
    )
    await callback.message.edit_text(text, reply_markup=get_stats_keyboard(user[10]))

@router.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    from keyboards.profile import get_profile_keyboard
    user = get_user_profile(callback.from_user.id)
    text = (
        f"🏰 Добро пожаловать, *{callback.from_user.username or 'Герой'}*, в хроники Реального Мира!\n\n"
        f"🧾 Профиль:\n"
        f"— 🪓 Сила: {user[2]}\n"
        f"— 🤸 Ловкость: {user[3]}\n"
        f"— 🛡️ Выносливость: {user[4]}\n"
        f"— 👁️ Восприятие: {user[5]}\n"
        f"— 📚 Интеллект: {user[6]}\n"
        f"— 🎭 Харизма: {user[7]}\n"
        f"— 🔥 Сила Воли: {user[8]}"
    )
    await callback.message.edit_text(text, reply_markup=get_profile_keyboard(), parse_mode="Markdown")

@router.callback_query(lambda c: c.data.startswith("inc_"))
async def increment_stat(callback: CallbackQuery):
    stat_map = {
        "inc_strength": "strength",
        "inc_agility": "agility",
        "inc_endurance": "endurance",
        "inc_perception": "perception",
        "inc_intelligence": "intelligence",
        "inc_charisma": "charisma",
        "inc_willpower": "willpower"
    }

    stat = stat_map.get(callback.data)
    user_id = callback.from_user.id

    if not stat:
        await callback.answer("Неизвестная характеристика.")
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT {stat}, free_points FROM users WHERE user_id = ?", (user_id,))
    current_value, free_points = cursor.fetchone()

    if free_points > 0:
        cursor.execute(f"""
            UPDATE users
            SET {stat} = ?, free_points = ?
            WHERE user_id = ?
        """, (current_value + 1, free_points - 1, user_id))
        conn.commit()
        await callback.answer(f"{stat.capitalize()} увеличена!")
    else:
        await callback.answer("Нет свободных очков!")
    
    conn.close()
    await stats_callback(callback)

@router.callback_query(lambda c: c.data == "random_distribute")
async def random_distribute_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Получим количество свободных очков
    cursor.execute("SELECT free_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row or row[0] == 0:
        await callback.answer("Нет очков для распределения!")
        conn.close()
        return

    points = row[0]
    stat_names = ["strength", "agility", "endurance", "perception", "intelligence", "charisma", "willpower"]
    distribution = {stat: 0 for stat in stat_names}

    for _ in range(points):
        stat = random.choice(stat_names)
        distribution[stat] += 1

    for stat, value in distribution.items():
        if value > 0:
            cursor.execute(f"""
                UPDATE users
                SET {stat} = {stat} + ?, free_points = free_points - ?
                WHERE user_id = ?
            """, (value, value, user_id))

    conn.commit()
    conn.close()

    await callback.answer("Очки распределены случайным образом!")
    await stats_callback(callback)