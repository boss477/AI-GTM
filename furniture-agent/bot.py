"""
Furniture Lead Agent - Telegram Bot
Telegram bot for hunting furniture sales leads
"""

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from agno_agent import run_agent
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_message = """
🪑 *Furniture Lead Hunter Bot*

Find new buildings and offices with potential to sell furniture!

*Commands:*
/hunt \<City\> \<Segment\> - Search for leads
/segments - View available segments
/help - Get help

*Example:*
/hunt Chennai Office
/hunt Mumbai Hotel
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_message,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_message = """
🆘 *Help*

*How to use:*

1. /hunt \<City\> \<Segment\>

Examples:
• /hunt Chennai Office
• /hunt Bangalore Coworking
• /hunt Mumbai Hotel

2. /segments
   - View all available segment types

*Segments:*
• Office - Corporate offices
• Coworking - Shared workspaces  
• Hotel - Hotels, resorts
• Restaurant - Restaurants, cafes
• Residential - Apartments
• Retail - Stores, malls

*Notes:*
• City is required
• Segment defaults to Office if not specified
• Maximum 10 results per search
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message,
        parse_mode="Markdown"
    )


async def segments_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /segments command."""
    segments_message = """
📋 *Available Segments*

1. *Office* - Corporate offices, business parks
2. *Coworking* - Shared workspaces, incubators
3. *Hotel* - Hotels, resorts, hospitality
4. *Restaurant* - Restaurants, cafes, dining
5. *Residential* - Apartments, housing complexes
6. *Retail* - Stores, malls, showrooms

*Usage:* /hunt \<City\> \<Segment\>
Example: /hunt Delhi Restaurant
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=segments_message,
        parse_mode="Markdown"
    )


async def hunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hunt command."""
    args = context.args
    
    if not args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please provide a city and segment!\n\nUsage: /hunt <City> <Segment>\n\nExample: /hunt Chennai Office"
        )
        return
    
    # Parse arguments
    if len(args) >= 2:
        city = args[0]
        segment = args[1].capitalize()
    else:
        city = args[0]
        segment = "Office"  # Default segment
    
    # Validate segment
    valid_segments = ["Office", "Coworking", "Hotel", "Restaurant", "Residential", "Retail"]
    if segment not in valid_segments:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Invalid segment: {segment}\n\nValid segments: {', '.join(valid_segments)}"
        )
        return
    
    # Send initial message
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🔍 Hunting for {segment} leads in {city}..."
    )
    
    try:
        # Run the LangGraph workflow. It searches, scores, filters, and saves leads.
        graph_response = run_agent(
            f"Find {segment.lower()} furniture leads in {city}, limit to 10"
        )
        leads = graph_response.state.get("leads", [])
        
        if not leads:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ No leads found for {segment} in {city}.\n\nTry a different city or segment."
            )
            return
        
        # Build response message
        response = f"🎯 *Found {len(leads)} leads for {segment} in {city}*\\n\\n"
        
        for i, lead in enumerate(leads, 1):
            # Score emoji
            score = lead["intent_score"]
            if score >= 9:
                emoji = "🟢"
            elif score >= 7:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            response += f"{i}. *{lead['company']}* {emoji} {score}/10\\n"
            response += f"   🌐 {lead['website']}\\n"
            response += f"   👤 {lead['decision_maker']}\\n\\n"
        
        # Send response (Telegram has message length limits)
        if len(response) > 4000:
            # Split into multiple messages
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=part,
                    parse_mode="Markdown"
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response,
                parse_mode="Markdown"
            )
        
        # Confirmation
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Leads saved to database!"
        )
        
    except Exception as e:
        logger.error(f"Error in hunt_command: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}\n\nPlease check your API configuration."
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown messages."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I didn't understand that. Use /help for available commands."
    )


def main():
    """Start the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token or token == "your_telegram_bot_token_here":
        print("❌ Please set TELEGRAM_BOT_TOKEN in .env file")
        return
    
    # Create application
    application = ApplicationBuilder().token(token).build()
    
    # Add handlers
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_command)
    segments_handler = CommandHandler('segments', segments_command)
    hunt_handler = CommandHandler('hunt', hunt_command)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(segments_handler)
    application.add_handler(hunt_handler)
    application.add_handler(echo_handler)
    
    print("🤖 Furniture Lead Hunter Bot is running...")
    print("Press Ctrl+C to stop")
    
    # Start polling
    application.run_polling()


if __name__ == '__main__':
    main()
