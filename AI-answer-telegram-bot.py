from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import asyncio
import logging

name = "main"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)

# Replace with your BotFather token
TOKEN = '7821821194:AAGCY_8otq9H05SLoix2Rs75BdT2T6LoAAk'
# Replace with your n8n webhook URL
N8N_WEBHOOK_URL = 'https://hook.eu2.make.com/6un66fo7c57fryq79xqpjenq1t47qh4g'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='1')],
        [InlineKeyboardButton("No", callback_data='2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

async def send_to_n8n(data):
    timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout
    logger.info(f"Sending data to n8n: {data}")
    logger.info(f"Using webhook URL: {N8N_WEBHOOK_URL}")
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(N8N_WEBHOOK_URL, json=data) as response:
                response_text = await response.text()
                logger.info(f"n8n response: {response_text}")
                logger.info(f"Response status: {response.status}")
                return response_text
        except asyncio.TimeoutError:
            logger.warning("Timeout while sending to n8n")
            return None
        except Exception as e:
            logger.error(f"Error sending to n8n: {e}")
            return None

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        # First answer the callback query to prevent timeout
        await query.answer()
        
        # Prepare data to send to n8n
        n8n_data = {
            "text": query.message.caption,
            "massage_id": query.message.id,
            "option": query.data,
            "chat_id": update.effective_chat.id,
            "user_id": update.effective_user.id,
            "username": update.effective_user.username
        }
        
        logger.info("Button clicked, preparing to send data to n8n")
        # Send to n8n in the background
        asyncio.create_task(send_to_n8n(n8n_data))
        
        # Update the message
        await query.edit_message_caption(text=f"Done!")
        
    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        try:
            await query.answer("Sorry, something went wrong. Please try again.")
        except:
            pass

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    
    application.run_polling()

if __name__ == '__main__':
    main()
