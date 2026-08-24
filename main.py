"""Simple Telegram force-subscription bot built with pyTelegramBotAPI."""

import os
import threading
import traceback

from flask import Flask
import telebot
from telebot import types


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_USERNAME = "@LearnEnglilsh"
CHANNEL_LINK = "https://t.me/LearnEnglilsh"
EXCLUSIVE_CONTENT_LINK = "https://t.me/+-f7N5sFp2Q4wYmRl"

PORT = int(os.getenv("PORT", "8080"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured in Secrets.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


@app.get("/")
def health_check() -> tuple[str, int]:
    return "Telegram bot is running", 200


def run_keep_alive_server() -> None:
    """Run Flask in the background so the process remains reachable."""
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def welcome_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
        types.InlineKeyboardButton(
            "✅ I joined — check again",
            callback_data="cb_check",
        ),
    )
    return keyboard


@bot.message_handler(commands=["start"])
def start_command(message: types.Message) -> None:
    bot.send_message(
        message.chat.id,
        "👋 <b>Welcome!</b>\n\n"
        "Please join our channel, then click "
        "<b>I joined — check again</b>.",
        parse_mode="HTML",
        reply_markup=welcome_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data == "cb_check")
def check_subscription(call: types.CallbackQuery) -> None:
    # Acknowledge the callback before performing the Telegram API request.
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in {"member", "administrator", "creator"}:
            bot.send_message(
                call.message.chat.id,
                "✅ <b>Verification successful!</b>\n\n"
                f"Exclusive Content: {EXCLUSIVE_CONTENT_LINK}",
                parse_mode="HTML",
            )
        else:
            bot.answer_callback_query(
                call.id,
                "You haven't joined the channel yet.",
                show_alert=True,
            )
    except Exception:
        traceback.print_exc()
        try:
            bot.answer_callback_query(
                call.id,
                "Unable to verify your membership. Please try again.",
                show_alert=True,
            )
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    threading.Thread(target=run_keep_alive_server, daemon=True).start()
    print(f"Starting Telegram bot with keep-alive server on port {PORT}...")
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception:
        traceback.print_exc()
        raise
