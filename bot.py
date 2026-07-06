import os
import logging
import sys

# Try to import telegram, if fails, install it
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        ContextTypes,
        CallbackQueryHandler,
        MessageHandler,
        filters
    )
    from deep_translator import GoogleTranslator
except ImportError as e:
    print(f"Missing module: {e}")
    print("Installing dependencies...")
    os.system(f"{sys.executable} -m pip install python-telegram-bot==20.7 deep-translator==1.11.4")
    # Reload the modules
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        ContextTypes,
        CallbackQueryHandler,
        MessageHandler,
        filters
    )
    from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("❌ No bot token found. Set TELEGRAM_BOT_TOKEN environment variable.")
    sys.exit(1)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh-CN': 'Chinese (Simplified)',
    'ja': 'Japanese', 'ar': 'Arabic', 'hi': 'Hindi', 'ko': 'Korean',
    'nl': 'Dutch', 'pl': 'Polish', 'tr': 'Turkish', 'vi': 'Vietnamese',
    'th': 'Thai', 'id': 'Indonesian', 'ms': 'Malay', 'sw': 'Swahili'
}

# Store user language preferences
user_languages = {}

def get_language_name(code):
    return SUPPORTED_LANGUAGES.get(code, code)

def get_user_language(user_id):
    return user_languages.get(user_id, 'en')

def create_language_keyboard():
    """Create inline keyboard with language options"""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 Spanish", callback_data='lang_es'),
            InlineKeyboardButton("🇫🇷 French", callback_data='lang_fr')
        ],
        [
            InlineKeyboardButton("🇩🇪 German", callback_data='lang_de'),
            InlineKeyboardButton("🇮🇹 Italian", callback_data='lang_it'),
            InlineKeyboardButton("🇵🇹 Portuguese", callback_data='lang_pt')
        ],
        [
            InlineKeyboardButton("🇷🇺 Russian", callback_data='lang_ru'),
            InlineKeyboardButton("🇨🇳 Chinese", callback_data='lang_zh-CN'),
            InlineKeyboardButton("🇯🇵 Japanese", callback_data='lang_ja')
        ],
        [
            InlineKeyboardButton("🇸🇦 Arabic", callback_data='lang_ar'),
            InlineKeyboardButton("🇮🇳 Hindi", callback_data='lang_hi'),
            InlineKeyboardButton("🇰🇷 Korean", callback_data='lang_ko')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with language selection"""
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_languages:
        user_languages[user_id] = 'en'
    
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to Language66 Translator Bot 🌍\n\n"
        "I can translate any text into your preferred language.\n\n"
        "How to use:\n"
        "1️⃣ Select your target language below\n"
        "2️⃣ Send me any text\n"
        "3️⃣ I'll translate it instantly!\n\n"
        f"Current language: {get_language_name(get_user_language(user_id))}\n\n"
        "Commands:\n"
        "/start - Show menu\n"
        "/help - Show help\n"
        "/setlang - Change language\n"
        "/lang - Show current language"
    )
    
    keyboard = create_language_keyboard()
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = (
        "🆘 Help & Commands\n\n"
        "Features:\n"
        "• Translate to 20+ languages\n"
        "• Simple button selection\n"
        "• Remembers your preference\n\n"
        "Commands:\n"
        "/start - Show menu\n"
        "/help - Show help\n"
        "/setlang - Change language\n"
        "/lang - Show current language\n\n"
        "Just send any text and I'll translate it!"
    )
    await update.message.reply_text(help_text)

async def set_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection"""
    keyboard = create_language_keyboard()
    await update.message.reply_text(
        "🌍 Choose your target language:",
        reply_markup=keyboard
    )

async def show_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current language"""
    user_id = update.effective_user.id
    lang_code = get_user_language(user_id)
    lang_name = get_language_name(lang_code)
    
    await update.message.reply_text(
        f"🌐 Your current language: {lang_name}\n"
        f"To change it, use /setlang"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data.startswith('lang_'):
        lang_code = data.replace('lang_', '')
        if lang_code in SUPPORTED_LANGUAGES:
            user_languages[user_id] = lang_code
            lang_name = get_language_name(lang_code)
            
            await query.edit_message_text(
                f"✅ Language set to: {lang_name}\n\n"
                f"Now send me any text to translate to {lang_name}!"
            )

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate incoming messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if not text or len(text.strip()) < 2:
        return
    
    target_lang = get_user_language(user_id)
    target_name = get_language_name(target_lang)
    
    try:
        translator = GoogleTranslator(target=target_lang)
        translated = translator.translate(text)
        
        reply = f"🌍 Translation to {target_name}:\n\n{translated}"
        await update.message.reply_text(reply)
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ Translation failed. Please try again."
        )

def main():
    """Start the bot"""
    logger.info("🚀 Starting Language66 Translator Bot...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("setlang", set_lang_command))
    app.add_handler(CommandHandler("lang", show_language))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
