from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading
import json
import os

# -----------------------------
# Flask Keep-Alive
# -----------------------------
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "✅ Pancono Airdrop Bot is Alive!"

def run():
    app_flask.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# -----------------------------
# Database Setup
# -----------------------------
DB_FILE = "database.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# Global Receiver / Admin
# -----------------------------
GLOBAL_RECEIVER_ID = 111111111  # 🔴 Replace with your Telegram ID

# -----------------------------
# /start Command
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args  # referral args
    
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {"balance": 0, "referred_by": None, "referrals": 0}
        
        # If referral exists
        if args:
            referrer_id = args[0]
            if referrer_id in db["users"] and referrer_id != user_id:
                db["users"][user_id]["referred_by"] = referrer_id
                db["users"][referrer_id]["balance"] += 1
                db["users"][referrer_id]["referrals"] += 1
        
        # New user reward
        db["users"][user_id]["balance"] += 1
        
        # Global receiver reward
        if str(GLOBAL_RECEIVER_ID) in db["users"]:
            db["users"][str(GLOBAL_RECEIVER_ID)]["balance"] += 1
        else:
            db["users"][str(GLOBAL_RECEIVER_ID)] = {"balance": 1, "referred_by": None, "referrals": 0}
        
        save_db(db)
    
    # Inline buttons
    keyboard = [
        [InlineKeyboardButton("📊 Account", callback_data="account")],
        [InlineKeyboardButton("🌐 Open App", url="https://f565c7f5-f513-4022-b596-a3cc0126783a-00-18vszwex2izzw.sisko.replit.dev/")]
    ]
    
    # Add admin panel button only for global user
    if user_id == str(GLOBAL_RECEIVER_ID):
        keyboard.append([InlineKeyboardButton("🛠 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome to Pancono Airdrop Bot!", reply_markup=reply_markup)

# -----------------------------
# Handle Inline Button Clicks
# -----------------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    db = load_db()
    
    if query.data == "account":
        balance = db["users"][user_id]["balance"]
        referrals = db["users"][user_id]["referrals"]
        referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
        
        text = (
            f"👤 *Your Account*\n\n"
            f"💰 Balance: {balance} PANNO\n"
            f"👥 Referrals: {referrals}\n"
            f"🔗 Referral Link: {referral_link}"
        )
        await query.answer()
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif query.data == "admin" and user_id == str(GLOBAL_RECEIVER_ID):
        admin_balance = db["users"][user_id]["balance"]  # Mr A global earnings
        total_users = len(db["users"])
        
        text = (
            f"🛠 *Admin Panel*\n\n"
            f"👑 Global Earnings (Mr A): {admin_balance} PANNO\n"
            f"👥 Total Registered Users: {total_users}"
        )
        await query.answer()
        await query.edit_message_text(text, parse_mode="Markdown")

# -----------------------------
# Main
# -----------------------------
def main():
    keep_alive()  # Start Flask server in background
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
