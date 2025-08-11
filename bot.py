import os
import logging
import json
import gspread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load .env locally (Render ignores this, it uses env vars)
load_dotenv()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # your Telegram ID
SHEET_NAME = os.getenv("SHEET_NAME", "Orders")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_JSON", "service_account.json")

# Google Sheets auth
gc = gspread.service_account(filename=GOOGLE_CREDS_FILE)
sheet = gc.open(SHEET_NAME).worksheet("Orders")

# ---------------- Google Sheets Menu Loader ----------------
def fetch_menu_from_sheet():
    try:
        menu_sheet = gc.open(SHEET_NAME).worksheet("Menu")
        rows = menu_sheet.get_all_values()
        # Expect: name, code in first two columns, skip header
        menu = [(row[0], row[1]) for row in rows[1:] if row and row[0] and row[1]]
        if not menu:
            logger.warning("Menu sheet is empty or misformatted.")
        return menu
    except Exception as e:
        logger.error(f"Error loading menu: {e}")
        return []

def menu_keyboard():
    MENU = fetch_menu_from_sheet()
    buttons = [[InlineKeyboardButton(name, callback_data=f"item|{code}")] for (name, code) in MENU]
    return InlineKeyboardMarkup(buttons)

# ---------------- Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please choose an item:", reply_markup=menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    if data[0] == "item":
        context.user_data["item"] = data[1]
        await query.edit_message_text("Please enter quantity:")

async def quantity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qty_text = update.message.text
    if not qty_text.isdigit():
        await update.message.reply_text("Please enter a valid number:")
        return

    context.user_data["quantity"] = int(qty_text)
    await update.message.reply_text("Please enter your name:")

    return

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name

    # Save order
    order = [
        context.user_data.get("name"),
        context.user_data.get("item"),
        context.user_data.get("quantity")
    ]
    sheet.append_row(order)

    await update.message.reply_text("? Order placed! Thank you.")

    # Notify admin
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"?? New order:\nName: {order[0]}\nItem: {order[1]}\nQuantity: {order[2]}"
        )

# ---------------- Main ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^item\\|"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
