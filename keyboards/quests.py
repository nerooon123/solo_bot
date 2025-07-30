from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_quests_keyboard(page, total, page_size, quest_id=None, completed=False):
    builder = InlineKeyboardBuilder()
    if quest_id and not completed:
        builder.button(text="✅ Выполнить", callback_data=f"complete_{quest_id}_{page}")
    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"quests_page_{page-1}")
    if (page + 1) * page_size < total:
        builder.button(text="➡️ Вперёд", callback_data=f"quests_page_{page+1}")
    builder.button(text="🔙 Назад", callback_data="back_to_profile")
    return builder.as_markup()