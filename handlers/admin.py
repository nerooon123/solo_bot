from aiogram import Router, types
from aiogram.filters import Command
from database import add_quest, add_skill, add_item
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS

router = Router()

class QuestAdd(StatesGroup):
    title = State()
    description = State()
    difficulty = State()
    goal = State()
    reward = State()

@router.message(Command("addquest"))
async def cmd_addquest(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет доступа.")
        return
    await message.answer("Введите название квеста:")
    await state.set_state(QuestAdd.title)

@router.message(QuestAdd.title)
async def quest_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание квеста:")
    await state.set_state(QuestAdd.description)

@router.message(QuestAdd.description)
async def quest_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите сложность (Легко, Средне, Сложно, Эксперт):")
    await state.set_state(QuestAdd.difficulty)

@router.message(QuestAdd.difficulty)
async def quest_difficulty(message: types.Message, state: FSMContext):
    await state.update_data(difficulty=message.text)
    await message.answer("Введите цель квеста:")
    await state.set_state(QuestAdd.goal)

@router.message(QuestAdd.goal)
async def quest_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.answer(
        "Введите награду для квеста.\n\n"
        "Примеры:\n"
        "XP +10 — опыт\n"
        "сила +1 — характеристика\n"
        "ловкость +1 — характеристика\n"
        "восприятие +1 — характеристика\n"
        "харизма +1 — характеристика\n"
        "сила воли +1 — характеристика\n"
        "интеллект +1 — характеристика\n"
        "выносливость +1 — характеристика\n"
        "нераспределенные очки +2 — свободные очки\n"
        "навык: Программирование +1 — добавить/повысить навык\n"
        "предмет: Мче бога +1 — дать предмет за квест (сначало надо добавить этот предмет через /additem\n"
        "Можно комбинировать через запятую: XP +10, интеллект +1, навык: Программирование +1"
    )
    await state.set_state(QuestAdd.reward)

@router.message(QuestAdd.reward)
async def quest_reward(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_quest(
        data["title"],
        data["description"],
        data["difficulty"],
        data["goal"],
        message.text
    )
    await message.answer("Квест добавлен!")
    await state.clear()

class SkillAdd(StatesGroup):
    name = State()
    description = State()

@router.message(Command("addskill"))
async def cmd_addskill(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет доступа.")
        return
    await message.answer("Введите название навыка:")
    await state.set_state(SkillAdd.name)

@router.message(SkillAdd.name)
async def skill_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание навыка:")
    await state.set_state(SkillAdd.description)

@router.message(SkillAdd.description)
async def skill_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_skill(data["name"], message.text)
    await message.answer("Навык добавлен!")
    await state.clear()

class ItemAdd(StatesGroup):
    name = State()
    quality = State()
    description = State()

@router.message(Command("additem"))
async def cmd_additem(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет доступа.")
        return
    await message.answer("Введите название предмета:")
    await state.set_state(ItemAdd.name)

@router.message(ItemAdd.name)
async def item_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите качество предмета (обычный, необычный, особый, редкий, исключительный, легендарный):")
    await state.set_state(ItemAdd.quality)

@router.message(ItemAdd.quality)
async def item_quality(message: types.Message, state: FSMContext):
    await state.update_data(quality=message.text)
    await message.answer("Введите описание предмета:")
    await state.set_state(ItemAdd.description)

@router.message(ItemAdd.description)
async def item_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_item(data["name"], data["quality"], message.text)
    await message.answer("Предмет добавлен!")
    await state.clear()