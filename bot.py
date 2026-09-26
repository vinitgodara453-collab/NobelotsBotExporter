"""
==============================================================================
🤖 NOBELOTS ACC STORE TELEGRAM BOT (PYTHON IMPLEMENTATION)
==============================================================================
Framework: pyTelegramBotAPI (telebot) / Python 3.10+
Install: pip install pyTelegramBotAPI requests python-dotenv qrcode
Run: python bot.py
==============================================================================
"""

import os
import json
import sqlite3
import requests
from dotenv import load_dotenv
import telebot
from telebot import types

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
SMM_API_URL = os.getenv("SMM_API_URL", "https://indiansmartpanel.com/api/v2")
SMM_API_KEY = os.getenv("SMM_API_KEY", "")
SMS_ACTIVATE_KEY = os.getenv("SMS_ACTIVATE_KEY", "")
UPI_ID = os.getenv("UPI_ID", "merchant@upi")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not provided in .env file!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE SETUP (SQLite) ---
conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance REAL DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    referred_by INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT,
    price REAL,
    category TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,
    credential TEXT,
    is_sold INTEGER DEFAULT 0
)
""")
conn.commit()

# Pre-seed default products if empty
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    sample_products = [
        ("tg-aged", "Telegram Aged 2022 Account", 85.0, "Telegram"),
        ("netflix-uhd", "Netflix 4K UHD 1 Month", 79.0, "OTT"),
        ("insta-aged", "Instagram 2018 Aged Account", 120.0, "Social")
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", sample_products)
    # Add sample stock
    cursor.execute("INSERT INTO stock (product_id, credential) VALUES ('tg-aged', 'session_data_sample_1')")
    cursor.execute("INSERT INTO stock (product_id, credential) VALUES ('netflix-uhd', 'netflix_user@gmail.com:pass123:PIN_4482')")
    conn.commit()


def get_user(user_id, username=""):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id, username, balance) VALUES (?, ?, 0)", (user_id, username))
        conn.commit()
        return {"user_id": user_id, "username": username, "balance": 0.0, "total_orders": 0}
    return {"user_id": row[0], "username": row[1], "balance": row[2], "total_orders": row[3]}


# --- KEYBOARDS ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("🛒 Buy Accounts", callback_data="menu_accounts")
    b2 = types.InlineKeyboardButton("📲 OTP Numbers", callback_data="menu_otp")
    b3 = types.InlineKeyboardButton("⚡ SMM Services", callback_data="menu_smm")
    b4 = types.InlineKeyboardButton("💰 Add Funds (UPI)", callback_data="menu_deposit")
    b5 = types.InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
    b6 = types.InlineKeyboardButton("📞 Support", callback_data="support")
    markup.add(b1, b2, b3, b4, b5, b6)
    return markup


@bot.message_handler(commands=['start'])
def start_handler(message):
    user = get_user(message.from_user.id, message.from_user.username)
    text = (
        f"👋 <b>Welcome, {message.from_user.first_name}!</b>\n\n"
        f"🤖 <b>Nobelots Acc Store Bot</b>\n"
        f"Buy aged accounts, virtual OTP numbers & SMM boosts instantly.\n\n"
        f"💰 <b>Your Balance:</b> ₹{user['balance']:.2f}\n"
        f"🆔 <b>Your ID:</b> <code>{message.from_user.id}</code>"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu_markup())


@bot.callback_query_handler(func=lambda call: call.data == "menu_accounts")
def accounts_menu(call):
    cursor.execute("SELECT p.id, p.name, p.price, COUNT(s.id) FROM products p LEFT JOIN stock s ON p.id = s.product_id AND s.is_sold = 0 GROUP BY p.id")
    rows = cursor.fetchall()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for prod_id, name, price, stock_count in rows:
        tag = f"[{stock_count} In Stock]" if stock_count > 0 else "[Sold Out]"
        markup.add(types.InlineKeyboardButton(f"{name} - ₹{price} {tag}", callback_data=f"view_prod_{prod_id}"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text("🛒 <b>Select Account to Buy:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("view_prod_"))
def view_product(call):
    prod_id = call.data.replace("view_prod_", "")
    cursor.execute("SELECT id, name, price FROM products WHERE id = ?", (prod_id,))
    prod = cursor.fetchone()
    if not prod:
        return bot.answer_callback_query(call.id, "Product not found!")

    cursor.execute("SELECT COUNT(*) FROM stock WHERE product_id = ? AND is_sold = 0", (prod_id,))
    stock_count = cursor.fetchone()[0]

    markup = types.InlineKeyboardMarkup()
    if stock_count > 0:
        markup.add(types.InlineKeyboardButton(f"⚡ Confirm Purchase (₹{prod[2]})", callback_data=f"buy_now_{prod_id}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="menu_accounts"))

    text = (
        f"📦 <b>{prod[1]}</b>\n\n"
        f"💵 <b>Price:</b> ₹{prod[2]}\n"
        f"📊 <b>In Stock:</b> {stock_count} units\n\n"
        f"Instant delivery on payment deduction."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_now_"))
def buy_product_now(call):
    prod_id = call.data.replace("buy_now_", "")
    user_id = call.from_user.id
    user = get_user(user_id)

    cursor.execute("SELECT price, name FROM products WHERE id = ?", (prod_id,))
    prod = cursor.fetchone()
    if not prod:
        return

    price, name = prod[0], prod[1]
    if user['balance'] < price:
        return bot.answer_callback_query(call.id, "❌ Insufficient balance! Please deposit via UPI.", show_alert=True)

    cursor.execute("SELECT id, credential FROM stock WHERE product_id = ? AND is_sold = 0 LIMIT 1", (prod_id,))
    stock_row = cursor.fetchone()
    if not stock_row:
        return bot.answer_callback_query(call.id, "❌ Out of stock!", show_alert=True)

    stock_id, credential = stock_row[0], stock_row[1]

    # Deduct and mark sold
    cursor.execute("UPDATE users SET balance = balance - ?, total_orders = total_orders + 1 WHERE user_id = ?", (price, user_id))
    cursor.execute("UPDATE stock SET is_sold = 1 WHERE id = ?", (stock_id,))
    conn.commit()

    bot.answer_callback_query(call.id, "✅ Order Placed Successfully!")
    success_text = (
        f"🎉 <b>Order Successful!</b>\n\n"
        f"📦 <b>Item:</b> {name}\n"
        f"💵 <b>Paid:</b> ₹{price}\n\n"
        f"🔑 <b>Your Account Details:</b>\n"
        f"<code>{credential}</code>"
    )
    bot.send_message(call.message.chat.id, success_text)


@bot.callback_query_handler(func=lambda call: call.data == "menu_deposit")
def deposit_menu(call):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=NobelotsStore%26cu=INR"
    caption = (
        f"💰 <b>Add Balance via UPI QR</b>\n\n"
        f"💳 <b>UPI ID:</b> <code>{UPI_ID}</code>\n"
        f"1. Kisi bhi UPI App se pay karein.\n"
        f"2. 12-digit UTR number note karein.\n"
        f"3. Niche button click karke UTR enter karein."
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 Submit 12-Digit UTR", callback_data="submit_utr"))
    markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    bot.send_photo(call.message.chat.id, qr_url, caption=caption, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def return_main(call):
    user = get_user(call.from_user.id)
    text = f"🤖 <b>Nobelots Acc Store Bot</b>\nBalance: ₹{user['balance']:.2f}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())


print("🚀 Python Bot Started Successfully!")
bot.infinity_polling()
