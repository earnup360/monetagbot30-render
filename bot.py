import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from flask import Flask
from threading import Thread
import os

# --- FLASK SERVER (RENDER এ বট ২৪ ঘণ্টা চালু রাখার জন্য) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully on Render!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- আপনার টেলিগ্রাম বটের কোড ---
TOKEN = '8612505898:AAE-zKQIJl2XefI-DtbVBvtRKBgc_en406A'
bot = telebot.TeleBot(TOKEN)

bot_info = bot.get_me()
BOT_USERNAME = bot_info.username

WEB_APP_URL = 'https://earnup360.github.io/monetag30-user/'

REQUIRED_CHANNELS = [
    {"name": "Join Now", "id": "@AdPulse_Zone", "link": "https://t.me/AdPulse_Zone"},
    {"name": "Join Now 1", "id": "@ProfitPathInfo", "link": "https://t.me/ProfitPathInfo"}
]

def check_all_joined(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            status = bot.get_chat_member(channel["id"], user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            return False
    return True

def send_main_menu(chat_id, user_id, referrer_id=None):
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    markup = InlineKeyboardMarkup()
    
    final_web_url = WEB_APP_URL
    if referrer_id and referrer_id != "none":
        final_web_url = f"{WEB_APP_URL}?start={referrer_id}"
    
    btn_webapp = InlineKeyboardButton("📱 Open Web App", web_app=WebAppInfo(url=final_web_url))
    share_text = "Join this awesome bot and earn BDT (TK) directly!"
    btn_share = InlineKeyboardButton("🔗 Share Referral Link", url=f"https://t.me/share/url?url={ref_link}&text={share_text}")
    
    markup.add(btn_webapp)
    markup.add(btn_share)

    msg_text = (
        "✅ <b>স্বাগতম! ভেরিফিকেশন সফল হয়েছে।</b>\n\n"
        "নিচের বাটন থেকে আমাদের অ্যাপটি ওপেন করে কাজ শুরু করুন।\n\n"
        "🎁 <b>আপনার ইনভাইট/রেফারেল লিংক:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        "👆 <i>লিংকটি কপি করতে উপরের লিংকে ক্লিক করুন অথবা নিচের শেয়ার বাটনে ক্লিক করে বন্ধুদের ইনভাইট করুন।</i>"
    )
    bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    parts = message.text.split()
    referrer_id = parts[1] if len(parts) > 1 else "none"

    if check_all_joined(user_id):
        send_main_menu(message.chat.id, user_id, referrer_id)
    else:
        markup = InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS:
            btn_channel = InlineKeyboardButton(f"🔔 Join {channel['name']}", url=channel["link"])
            markup.add(btn_channel)

        btn_joined = InlineKeyboardButton("🟢 Joined All", callback_data=f"verify_{referrer_id}")
        markup.add(btn_joined)
        msg_text = "📢 <b>Welcome to Task Network</b>\n\n🤖 To continue using the bot, please join ALL our official channels."
        bot.send_message(message.chat.id, msg_text, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_"))
def verify_button_click(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    referrer_id = call.data.split("_")[1]

    if check_all_joined(user_id):
        bot.answer_callback_query(call.id, "✅ Verification Successful! Welcome.")
        bot.delete_message(chat_id, call.message.message_id)
        send_main_menu(chat_id, user_id, referrer_id)
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো সবগুলো চ্যানেলে জয়েন করেননি!", show_alert=True)

# --- বট স্টার্ট করা ---
print("সার্ভার এবং বট চালু হচ্ছে...")
bot.remove_webhook()
keep_alive()  # ফ্লাস্ক সার্ভার কল করা হলো
bot.polling(none_stop=True)
