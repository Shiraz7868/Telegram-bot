# main_bot.py

import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Replace 'YOUR_TELEGRAM_API_TOKEN' with your actual bot token from BotFather
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_API_TOKEN'

# Enable logging to see errors and bot activity in the console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Function ---
def get_youtube_video_id(url: str) -> str | None:
    """
    Extracts the YouTube video ID from a given URL using regex.
    Handles various YouTube URL formats (youtube.com, youtu.be, etc.).
    """
    # Regex to find the video ID in different YouTube URL formats
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    
    match = re.search(youtube_regex, url)
    
    if match:
        # The video ID is the last captured group
        return match.group(6)
    return None

# --- Bot Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Sends a welcome message to the user.
    """
    user = update.effective_user
    welcome_message = (
        f"خوش آمدید, {user.first_name}!\n\n"
        "میں ایک یوٹیوب تھمب نیل ڈاؤنلوڈر بوٹ ہوں۔\n\n"
        "مجھے کسی بھی یوٹیوب ویڈیو کا لنک بھیجیں اور میں آپ کو اس کا تھمب نیل بھیج دوں گا۔"
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for regular text messages.
    Checks if the message is a valid YouTube link and sends the thumbnail.
    """
    message_text = update.message.text
    logger.info(f"Received message: {message_text}")

    # Extract video ID from the received text
    video_id = get_youtube_video_id(message_text)

    if video_id:
        # If a valid video ID is found, construct the thumbnail URL
        # 'maxresdefault.jpg' provides the highest quality thumbnail (1280x720)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        logger.info(f"Found Video ID: {video_id}. Sending thumbnail: {thumbnail_url}")
        
        # Send a "typing..." action to let the user know the bot is working
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
        
        # Send the thumbnail image directly from the URL
        await update.message.reply_photo(
            photo=thumbnail_url,
            caption="یہ رہا آپ کا تھمب نیل! ✨"
        )
    else:
        # If no valid YouTube link is found
        logger.warning(f"Invalid link or text received: {message_text}")
        await update.message.reply_text(
            "معذرت، یہ ایک درست یوٹیوب لنک نہیں ہے۔\n\n"
            "براہ کرم ایک صحیح یوٹیوب ویڈیو کا لنک بھیجیں۔ مثال کے طور پر:\n"
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

# --- Main Function to Run the Bot ---
def main() -> None:
    """
    Starts the bot and sets up handlers.
    """
    # Create the Application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handler for the /start command
    application.add_handler(CommandHandler("start", start_command))

    # Add handler for all other text messages (to process YouTube links)
    # The `~filters.COMMAND` part ensures that this handler doesn't trigger for commands like /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    
    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
