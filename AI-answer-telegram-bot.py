from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import asyncio
import logging

# General logger setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
general_logger = logging.getLogger("bot")

# Bot token and webhook URL (replace with your own values)
BOT_TOKEN = '7821821194:AAGCY_8otq9H05SLoix2Rs75BdT2T6LoAAk'
WEBHOOK_URL = 'https://hook.eu2.make.com/6un66fo7c57fryq79xqpjenq1t47qh4g'

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
    general_logger.info(f"Sending payload to webhook: {payload}")
    general_logger.info(f"Using webhook URL: {WEBHOOK_URL}")
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                response_text = await response.text()
                general_logger.info(f"Webhook response: {response_text}")
                general_logger.info(f"Response status: {response.status}")
                return response_text
        except asyncio.TimeoutError:
            general_logger.warning("Timeout while sending to webhook")
            return None
        except Exception as e:
            general_logger.error(f"Error sending to webhook: {e}")
            return None

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        # Acknowledge the callback to avoid timeout
        await query.answer()
        
        # Prepare generic payload for webhook
        webhook_payload = {
            "text": query.message.caption,
            "message_id": query.message.id,
            "selected_option": query.data,
            "chat_id": update.effective_chat.id,
            "user_id": update.effective_user.id,
            "username": update.effective_user.username
        }
        
        general_logger.info("Button pressed, sending payload to webhook")
        # Send to webhook asynchronously
        asyncio.create_task(send_to_webhook(webhook_payload))
        
        # Update the message caption
        await query.edit_message_caption(text=f"Done!")
        
    except Exception as e:
        general_logger.error(f"Error in button handler: {e}")
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
