import logging
import random
import os
import threading
from flask import Flask # አዲስ መጨመሪያ
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. የአስማት ቁልፎች
TOKEN = "8814685966:AAGitN24CD-sWQXcybDu9bQjeNuC5OznjDQ"
ADMIN_ID = 7986264215

# --- ለ Render እንዳይተኛ የምንጨምረው 'የደወል' ክፍል ---
app = Flask('')
@app.route('/')
def home():
    return "እኔ ቦቱ ነኝ፣ አልተኛሁም!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)
# ---------------------------------------------

PAID_USERS_FILE = "paid_users.txt"

def get_paid_users():
    if not os.path.exists(PAID_USERS_FILE):
        return []
    with open(PAID_USERS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def add_paid_user(user_id):
    with open(PAID_USERS_FILE, "a") as f:
        f.write(f"{user_id}\n")

# ... (እዚህ ጋር ያሉት 100 ጥያቄዎች እንዳሉ ይቆያሉ) ...
EXAMS = {
    'Management': [{'q': '1. የአመራር የመጀመሪያው ተግባር ምንድነው?', 'o': ['ሀ. መቆጣጠር', 'ለ. ማቀድ', 'ሐ. መቅጠር'], 'a': 'ለ. ማቀድ'}],
    'Economics': [{'q': '1. ኤኮኖሚክስ ስለ ምን ያጠናል?', 'o': ['ሀ. ጤና', 'ለ. ስለ ሀብት ውስንነት', 'ሐ. ስለ ስፖርት'], 'a': 'ለ. ስለ ሀብት ውስንነት'}]
}

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data_store[user_id] = {'count': 0, 'score': 0}
    keyboard = [['Management', 'Economics']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👋 ሰላም! ID: {user_id}\nትምህርት ምረጥ።", reply_markup=reply_markup)

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    target_id = context.args[0]
    add_paid_user(target_id)
    await update.message.reply_text(f"✅ ID {target_id} አግብርያለሁ!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    paid_users = get_paid_users()
    if user_id not in user_data_store: user_data_store[user_id] = {'count': 0, 'score': 0}
    if user_id not in paid_users and user_data_store[user_id]['count'] >= 20:
        await update.message.reply_text(f"🛑 ነፃ ሙከራ አልቋል! ID: {user_id} ለ @papilololo ይላኩ።")
        return
    if text in EXAMS:
        context.user_data['current_exam'] = text
        await ask_random_question(update, context)
    elif 'current_exam' in context.user_data:
        last_q = context.user_data.get('last_q')
        if last_q and text in last_q['o']:
            user_data_store[user_id]['count'] += 1
            msg = "✅ ትክክል!" if text == last_q['a'] else f"❌ ተሳስተሃል! መልሱ: {last_q['a']}"
            await update.message.reply_text(f"{msg}\n📊 ተራ: {user_data_store[user_id]['count']}")
            await ask_random_question(update, context)

async def ask_random_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exam_type = context.user_data['current_exam']
    q = random.choice(EXAMS[exam_type])
    context.user_data['last_q'] = q
    reply_markup = ReplyKeyboardMarkup([q['o']], resize_keyboard=True)
    await update.message.reply_text(q['q'], reply_markup=reply_markup)

if __name__ == '__main__':
    # 1. 'ደወሉን' (Flask) ከበስተጀርባ እናስነሳው
    threading.Thread(target=run_flask).start()
    
    # 2. ቦቱን እናስነሳው (Render ላይ Proxy አያስፈልግም!)
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("activate", activate))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ሮቦቱ ስራ ጀምሯል...")
    application.run_polling()
