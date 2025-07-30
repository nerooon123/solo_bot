from aiogram import Router
from aiogram.types import CallbackQuery
from database import get_user_profile, add_user, get_quests_page, is_quest_completed, complete_quest, add_xp_and_level
from keyboards.profile import get_back_keyboard, get_profile_keyboard, get_stats_keyboard
from keyboards.quests import get_quests_keyboard
import sqlite3
import json
import random
import re

router = Router()

def safe_inventory(inv_raw):
    if not inv_raw or isinstance(inv_raw, int):
        return []
    if isinstance(inv_raw, str):
        try:
            return json.loads(inv_raw)
        except Exception:
            return []
    return []

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

    strength = user[2]
    intelligence = user[6]
    base_hp = 100
    base_mp = 100
    hp = int(base_hp * (1 + strength * 0.100))
    mp = int(base_mp * (1 + intelligence * 0.100))

    text = (
        f"🏰 Профиль игрока\n"
        f"Имя: {callback.from_user.username or 'Герой'}\n"
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

@router.callback_query(lambda c: c.data == "quests" or c.data.startswith("quests_page_"))
async def quests_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    page_size = 1
    if callback.data == "quests":
        page = 0
    else:
        page = int(callback.data.split("_")[-1])
    quests, total = get_quests_page(page, page_size)
    if not quests:
        await callback.message.edit_text("🗺️ Нет доступных квестов.", reply_markup=get_back_keyboard())
        return
    quest = quests[0]
    completed = is_quest_completed(user_id, quest[0])
    text = (
        f"#{quest[0]} | 📌 <b>{quest[1]}</b>\n"
        f"Описание: {quest[2]}\n"
        f"Сложность: {quest[3]}\n"
        f"Цель: {quest[4]}\n"
        f"Награда: {quest[5]}\n"
        f"\n{'✅ Выполнено' if completed else ''}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_quests_keyboard(page, total, page_size, quest_id=quest[0], completed=completed),
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data.startswith("complete_"))
async def complete_quest_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, quest_id, page = callback.data.split("_")
    quest_id = int(quest_id)
    page = int(page)
    if is_quest_completed(user_id, quest_id):
        await callback.answer("Квест уже выполнен!")
        return
    # Получаем награду
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT reward FROM quests WHERE id = ?", (quest_id,))
    reward = cursor.fetchone()[0]
    user = get_user_profile(user_id)
    xp = user[14]
    leveled_up = False
    new_level = None

    # XP и уровень
    if "XP" in reward:
        match = re.search(r'XP\s*\+(\d+)', reward)
        if match:
            xp_to_add = int(match.group(1))
            leveled_up, new_level = add_xp_and_level(user_id, xp_to_add)

    # Остальные награды
    if "интеллект" in reward:
        match = re.search(r'интеллект\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET intelligence = intelligence + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "выносливость" in reward:
        match = re.search(r'выносливость\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET endurance = endurance + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "нераспределенные очки" in reward:
        match = re.search(r'нераспределенные очки\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET free_points = free_points + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "навык:" in reward:
        skills = json.loads(user[9]) if user[9] else {}
        for part in reward.split(","):
            if "навык:" in part:
                match = re.search(r'навык:\s*([^\+]+)\+(\d+)', part)
                if match:
                    skill_name = match.group(1).strip()
                    skill_inc = int(match.group(2))
                    skills[skill_name] = skills.get(skill_name, 0) + skill_inc
        cursor.execute("UPDATE users SET skills = ? WHERE user_id = ?", (json.dumps(skills), user_id))
    if "сила" in reward:
        match = re.search(r'сила\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET strength = strength + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "ловкость" in reward:
        match = re.search(r'ловкость\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET agility = agility + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "восприятие" in reward:
        match = re.search(r'восприятие\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET perception = perception + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "харизма" in reward:
        match = re.search(r'харизма\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET charisma = charisma + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "сила воли" in reward:
        match = re.search(r'сила воли\s*\+(\d+)', reward)
        if match:
            cursor.execute("UPDATE users SET willpower = willpower + ? WHERE user_id = ?", (int(match.group(1)), user_id))
    if "предмет:" in reward:
        inventory = safe_inventory(user[17])
        for part in reward.split(","):
            if "предмет:" in part:
                match = re.search(r'предмет:\s*([^\+]+)', part)
                if match:
                    item_name = match.group(1).strip()
                    cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
                    item = cursor.fetchone()
                    if item:
                        inventory.append(item[0])
        cursor.execute("UPDATE users SET inventory = ? WHERE user_id = ?", (json.dumps(inventory), user_id))

    conn.commit()
    conn.close()
    complete_quest(user_id, quest_id)

    # Сообщение пользователю
    if leveled_up:
        await callback.answer(f"Квест выполнен! Уровень повышен до {new_level}!")
    else:
        await callback.answer("Квест выполнен! Награда получена.")
    await quests_callback(callback)

@router.callback_query(lambda c: c.data == "inventory")
async def inventory_callback(callback: CallbackQuery):
    user = get_user_profile(callback.from_user.id)
    inventory = safe_inventory(user[17])
    if not inventory:
        await callback.message.edit_text("🎒 Ваш инвентарь пуст.", reply_markup=get_back_keyboard())
        return
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    text = "🎒 Ваш инвентарь:\n"
    for item_id in inventory:
        cursor.execute("SELECT name, quality, description FROM items WHERE id = ?", (item_id,))
        name, quality, description = cursor.fetchone()
        color = {
            "обычный": "",
            "необычный": "🟩 <b>",
            "особый": "🟦 <b>",
            "редкий": "🟪 <b>",
            "исключительный": "🟥 <b>",
            "легендарный": "🟨 <b>"
        }.get(quality, "")
        end = "</b>" if color else ""
        text += f"{color}{name}{end} — {description}\n"
    conn.close()
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")


