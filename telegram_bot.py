# telegram_bot.py

import logging
import asyncio
import aiohttp
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from core.config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PsychoBot:
    def __init__(self):
        self.api_url = f"{Config.API_BASE_URL}/api/v1/psychology/chat"
        self.session = None
    
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        if self.session:
            await self.session.close()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
Welcome to PsychoHealer Bot!

I'm here to provide psychological support and guidance. 
Just send me a message about what's on your mind, and I'll help you through it.

Commands:
/help - Show help information
/clear - Clear our conversation history
        """
        await update.message.reply_text(welcome_msg.strip())
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """
How to use PsychoHealer Bot:

- Simply type your thoughts, feelings, or questions
- I'll provide supportive psychological guidance
- Our conversation is private and confidential

Examples:
- "I'm feeling anxious about work"
- "How can I manage stress better?"
- "I'm having trouble with relationships"

Commands:
/start - Welcome message
/help - This help message
/clear - Clear conversation history

Note: This is for general support, not professional therapy.
        """
        await update.message.reply_text(help_msg.strip())
    
    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        await update.message.reply_text("Conversation history cleared! Let's start fresh.")
    
    def format_youtube_videos(self, videos):
        """Format YouTube videos for Telegram message"""
        if not videos or len(videos) == 0:
            return ""
        
        video_text = "\n\n🎥 *Recommended Videos:*\n"
        for i, video in enumerate(videos[:3], 1):  # Limit to 3 videos to avoid message length issues
            title = video.get('title', 'Video')
            url = video.get('url', '')
            duration = video.get('duration', '')
            channel = video.get('channel', '')
            
            # Format each video
            video_line = f"{i}. [{title}]({url})"
            if duration:
                video_line += f" ({duration})"
            if channel:
                video_line += f" - {channel}"
            
            video_text += video_line + "\n"
        
        return video_text
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages"""
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        try:
            await self.init_session()
            
            # Call your API
            async with self.session.post(
                self.api_url,
                json={"query": user_message, "user_id": user_id},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Get the main response
                    bot_response = data.get('response', 'No response available')
                    
                    # Get YouTube videos
                    youtube_videos = data.get('youtube_videos', [])
                    
                    # Format the complete message
                    complete_message = bot_response
                    
                    # Add YouTube videos if available
                    if youtube_videos:
                        video_section = self.format_youtube_videos(youtube_videos)
                        complete_message += video_section
                    
                    # Send the complete message with videos
                    await update.message.reply_text(
                        complete_message,
                        parse_mode='Markdown',
                        disable_web_page_preview=False  # Enable link previews for videos
                    )
                    
                    # Send additional info about model used (for debugging)
                    model_used = data.get('model_used', '')
                    if model_used and context.args and '--debug' in context.args:
                        await update.message.reply_text(
                            f" Model used: {model_used}",
                            parse_mode='Markdown'
                        )
                
                else:
                    await update.message.reply_text(
                        "I'm having trouble right now. Please try again in a moment."
                    )
        
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error. Please try again."
            )
    
    async def setup_commands(self, app):
        """Set up bot commands menu"""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help"),
            BotCommand("clear", "Clear conversation history")
        ]
        await app.bot.set_my_commands(commands)
    
    def run(self):
        """Run the bot"""
        app = ApplicationBuilder().token(Config.TELEGRAM_BOT_KEY).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("clear", self.clear_history))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Set up commands after app is built
        async def post_init(app):
            await self.setup_commands(app)
        
        app.post_init = post_init
        
        # Cleanup on shutdown
        async def cleanup(app):
            await self.close_session()
        app.post_shutdown = cleanup
        
        logger.info("PsychoHealer Bot is starting...")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    bot = PsychoBot()
    bot.run()

    