import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Import our Unified Agent
from unified_agent import get_unified_agent

# Load Environment and Configure logger
load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the UI/Agent
agent = get_unified_agent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "👋 Hello! I am ARIA, your Strategist, Hunter, and Invoice assistant.\n\n"
    msg += "I'm currently connected to your local model (Qwen 3.5 9B).\n"
    msg += "You can ask me to search for leads, manage invoices, or analyze business strategy."
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return
    
    # Send a typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Run the agent logic
        # We use run_sync if it's blocking, but Agno.Agent is usually sync
        logger.info(f"User Request: {user_text}")
        response = agent.run(user_text)
        
        # Agno responses have a 'content' field or are string-like
        output = str(response.content if hasattr(response, 'content') else response)
        
        await update.message.reply_text(output, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(f"⚠️ Sorry, I encountered an error: {str(e)}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Downloads the photo from Telegram and sends it to the Qwen model for analysis."""
    photo_file = await update.message.photo[-1].get_file()
    
    # Send as binary to Agno for analysis
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Download file to memory
        import base64
        file_bytes = await photo_file.download_as_bytearray()
        base64_image = base64.b64encode(file_bytes).decode('utf-8')

        logger.info("Sending photo to Qwen for analysis...")
        
        # In Agno, we can provide image content in the run method
        # Format depends on model, but standard is a dict with type image_url
        response = agent.run(
            "Please analyze this image and provide a strategic summary based on your identity.",
            images=[f"data:image/jpeg;base64,{base64_image}"]
        )
        
        output = str(response.content if hasattr(response, 'content') else response)
        await update.message.reply_text(output, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error analyzing photo: {e}")
        await update.message.reply_text(f"⚠️ I received the photo, but had trouble analyzing it: {str(e)}")

if __name__ == '__main__':
    # Get token from .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env!")
        exit(1)

    # Build the Telegram application
    application = ApplicationBuilder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🚀 ARIA Telegram Bot is starting locally on port 8000...")
    print("Talk to your bot at t.me/vijau_bot")
    
    application.run_polling()
