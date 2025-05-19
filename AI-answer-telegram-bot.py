from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import asyncio

# Bot token and webhook URL (replace with your own values)
BOT_TOKEN = '7821821194:AAGCY_8otq9H05SLoix2Rs75BdT2T6LoAAk'
WEBHOOK_URL = 'https://hook.us2.make.com/ga8m169h9xkgxo3rcns84mr33xn5t8w2'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Display options to the user
    options = [
        [InlineKeyboardButton("Yes", callback_data='1')],
        [InlineKeyboardButton("No", callback_data='2')],
    ]
    markup = InlineKeyboardMarkup(options)
    await update.message.reply_text("Choose an option:", reply_markup=markup)

async def send_to_webhook(payload):
    timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                return await response.text()
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
        webhook_payload = {
            "text": query.message.caption,
            "message_id": query.message.id,
            "selected_option": query.data,
            "chat_id": update.effective_chat.id,
            "user_id": update.effective_user.id,
            "username": update.effective_user.username
        }
        asyncio.create_task(send_to_webhook(webhook_payload))
        await query.edit_message_caption(text=f"Done!")
    except Exception:
        try:
            await query.answer("Sorry, something went wrong. Please try again.")
        except:
            pass

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()

if __name__ == '__main__':
    run_bot()
