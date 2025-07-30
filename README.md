# 🤖 Solo Bot

Telegram RPG-бот с квестами, навыками, характеристиками и инвентарём.

## 🚀 Возможности

- 📜 Навыки и их прокачка
- 🧠 Характеристики персонажа
- 🗺️ Квесты с наградами (XP, характеристики, навыки, предметы)
- 🎒 Инвентарь с предметами разных качеств
- 👑 Админ-панель для добавления квестов, предметов, навыков

## 🛠️ Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/solo_bot.git
   cd solo_bot
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Укажите токен бота и ID администратора в `config.py`:
   ```python
   BOT_TOKEN = "ВАШ_ТОКЕН"
   ADMIN_IDS = [ВАШ_ID]
   ```

4. Запустите бота:
   ```bash
   python main.py
   ```

## 📝 Примеры команд для администратора

- `/addquest` — добавить квест
- `/additem` — добавить предмет
- `/addskill` — добавить навык

## 🏆 Качества предметов

- 🟩 Необычный
- 🟦 Особый
- 🟪 Редкий
- 🟥 Исключительный
- 🟨 Легендарный

## 📂 Структура проекта

```
solo_bot/
├── handlers/
│   ├── start.py
│   ├── callbacks.py
│   └── admin.py
├── keyboards/
│   ├── profile.py
│   └── quests.py
├── database.py
├── config.py
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```