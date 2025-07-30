from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📜 Навыки", callback_data="skills")
    builder.button(text="🧠 Характеристики", callback_data="stats")
    builder.button(text="🗺️ Квесты", callback_data="quests")
    builder.button(text="🎒 Инвентарь", callback_data="inventory")
    return builder.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back_to_profile")
    return builder.as_markup()

def get_stats_keyboard(free_points: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if free_points > 0:
        builder.button(text="➕ Сила", callback_data="inc_strength")
        builder.button(text="➕ Ловкость", callback_data="inc_agility")
        builder.button(text="➕ Выносливость", callback_data="inc_endurance")
        builder.button(text="➕ Восприятие", callback_data="inc_perception")
        builder.button(text="➕ Интеллект", callback_data="inc_intelligence")
        builder.button(text="➕ Харизма", callback_data="inc_charisma")
        builder.button(text="➕ Сила Воли", callback_data="inc_willpower")

        builder.adjust(3)
        
        builder.button(text="🎲 Распределить случайно", callback_data="random_distribute")

    builder.button(text="🔙 Назад", callback_data="back_to_profile")
    return builder.as_markup()
