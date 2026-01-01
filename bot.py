# ===============================
# МЕСТА ДЛЯ РЫБАЛКИ — ПРИМОРСКИЙ КРАЙ
# Telegram Bot (ONE FILE)
# ===============================

import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os

# ===== НАСТРОЙКИ =====
TOKEN = "8086546491:AAEoPQhptnG4s3mgs6IGFx5UkCTVER6PRps"
ADMINS = [319425268]  # <-- ВСТАВЬ СВОЙ TELEGRAM ID

DB = "fishing.db"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===== БАЗА =====
conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    fish TEXT,
    season TEXT,
    lat REAL,
    lon REAL,
    rating INTEGER DEFAULT 0,
    approved INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    media TEXT,
    link TEXT,
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    expires TEXT,
    approved INTEGER DEFAULT 0
)
""")

conn.commit()

# ===== КЛАВИАТУРЫ =====
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add("📍 Места", "🐟 По рыбе")
main_kb.add("➕ Добавить место", "🏆 Топ мест")
main_kb.add("📢 Объявления")

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add("🛂 Модерация мест", "📣 Модерация рекламы")

# ===== START =====
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (msg.from_user.id,))
    conn.commit()
    await msg.answer(
        "🎣 *Места для рыбалки — Приморский край*\n\n"
        "✔ Каталог мест\n"
        "✔ Карта\n"
        "✔ Поиск по рыбе\n"
        "✔ Реклама\n",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

# ===== ПРОСМОТР МЕСТ =====
@dp.message_handler(text="📍 Места")
async def list_places(msg: types.Message):
    cursor.execute("SELECT id, name FROM places WHERE approved=1")
    rows = cursor.fetchall()
    if not rows:
        await msg.answer("Пока нет добавленных мест.")
        return

    kb = InlineKeyboardMarkup()
    for r in rows:
        kb.add(InlineKeyboardButton(r[1], callback_data=f"place_{r[0]}"))
    await msg.answer("Выбери место:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("place_"))
async def place_view(call: types.CallbackQuery):
    pid = int(call.data.split("_")[1])
    cursor.execute("SELECT name, description, fish, season, lat, lon FROM places WHERE id=?", (pid,))
    p = cursor.fetchone()

    text = (
        f"📍 *{p[0]}*\n\n"
        f"{p[1]}\n\n"
        f"🐟 Рыба: {p[2]}\n"
        f"📅 Сезон: {p[3]}"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📍 2ГИС", url=f"https://2gis.ru/geo/{p[4]},{p[5]}"),
        InlineKeyboardButton("🗺 Яндекс", url=f"https://yandex.ru/maps/?pt={p[5]},{p[4]}&z=14"),
        InlineKeyboardButton("🌍 Google", url=f"https://maps.google.com/?q={p[4]},{p[5]}")
    )

    await call.message.answer(text, parse_mode="Markdown", reply_markup=kb)

# ===== ПО РЫБЕ =====
@dp.message_handler(text="🐟 По рыбе")
async def by_fish(msg: types.Message):
    cursor.execute("SELECT DISTINCT fish FROM places WHERE approved=1")
    fishes = cursor.fetchall()
    kb = InlineKeyboardMarkup()
    for f in fishes:
        kb.add(InlineKeyboardButton(f[0], callback_data=f"fish_{f[0]}"))
    await msg.answer("Выбери рыбу:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("fish_"))
async def fish_places(call: types.CallbackQuery):
    fish = call.data.split("_", 1)[1]
    cursor.execute("SELECT name FROM places WHERE fish=? AND approved=1", (fish,))
    rows = cursor.fetchall()
    text = "📍 Места:\n" + "\n".join([r[0] for r in rows])
    await call.message.answer(text)

# ===== ТОП =====
@dp.message_handler(text="🏆 Топ мест")
async def top(msg):
    cursor.execute("SELECT name, rating FROM places WHERE approved=1 ORDER BY rating DESC LIMIT 5")
    rows = cursor.fetchall()
    text = "🏆 *Топ мест:*\n\n"
    for r in row

