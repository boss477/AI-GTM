import os
import asyncio
import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Import our Unified Agent
from unified_agent import get_unified_agent
from unified_toolkit import UnifiedToolkit

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
    """Downloads the photo from Telegram and tracks state to handle 1st vs 2nd photo."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Track the number of photos sent in this session
    count = context.user_data.get('photo_count', 0)
    count += 1
    context.user_data['photo_count'] = count
    
    try:
        if count == 1:
            await update.message.reply_text("This furniture is not available right now.")
        else:
            # 2nd picture (or more): Upload and respond with random price
            photo_file = await update.message.photo[-1].get_file()
            file_bytes = await photo_file.download_as_bytearray()
            
            toolkit = UnifiedToolkit()
            public_url = toolkit.upload_furniture_image(bytes(file_bytes))
            
            if "Error" in public_url:
                await update.message.reply_text(f"⚠️ Failed to save image to storage: {public_url}")
            else:
                price = random.randint(5000, 25000)
                await update.message.reply_text(f"This furniture is available ✅ Wanna buy? Its price is Rs. {price:,}")
                
                # Generate formal Performa Invoice and send the real document
                inv_result = toolkit.create_telegram_invoice(public_url, price)
                if isinstance(inv_result, dict) and "absolute_pdf_path" in inv_result:
                    with open(inv_result["absolute_pdf_path"], "rb") as pdf_file:
                        await update.message.reply_document(
                            document=pdf_file,
                            filename=f"Invoice_{inv_result.get('invoice_number', 'PI')}.pdf",
                            caption="🧾 Here is the formal Performa Invoice for your request!"
                        )
                else:
                    await update.message.reply_text(f"⚠️ Could not generate invoice document: {inv_result}")
                
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await update.message.reply_text(f"⚠️ I received the photo, but had trouble linking it: {str(e)}")

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
    
    print("ARIA Telegram Bot is starting locally on port 8000...")
    print("Talk to your bot at t.me/vijau_bot")
    
    application.run_polling()
