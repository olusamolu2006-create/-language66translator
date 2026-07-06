import os
import logging
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
    exit(1)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh-CN': 'Chinese (Simplified)',
    'ja': 'Japanese', 'ar': 'Arabic', 'hi': 'Hindi', 'ko': 'Korean',
    'nl': 'Dutch', 'pl': 'Polish', 'tr': 'Turkish', 'vi': 'Vietnamese',
    'th': 'Thai', 'id': 'Indonesian', 'ms': 'Malay', 'sw': 'Swahili',
    'el': 'Greek', 'he': 'Hebrew', 'hu': 'Hungarian', 'cs': 'Czech'
}

# Store user language preferences (in-memory)
user_languages = {}

def get_language_name(code):
    """Get full language name from code"""
    return SUPPORTED_LANGUAGES.get(code, code)

def get_user_language(user_id):
    """Get user's preferred language, default to English"""
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
        ],
        [
            InlineKeyboardButton("🌍 More Languages", callback_data='more_languages')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_more_languages_keyboard():
    """Create keyboard with additional languages"""
    keyboard = [
        [
            InlineKeyboardButton("🇳🇱 Dutch", callback_data='lang_nl'),
            InlineKeyboardButton("🇵🇱 Polish", callback_data='lang_pl'),
            InlineKeyboardButton("🇹🇷 Turkish", callback_data='lang_tr')
        ],
        [
            InlineKeyboardButton("🇻🇳 Vietnamese", callback_data='lang_vi'),
            InlineKeyboardButton("🇹🇭 Thai", callback_data='lang_th'),
            InlineKeyboardButton("🇮🇩 Indonesian", callback_data='lang_id')
        ],
        [
            InlineKeyboardButton("🇲🇾 Malay", callback_data='lang_ms'),
            InlineKeyboardButton("🇰🇪 Swahili", callback_data='lang_sw'),
            InlineKeyboardButton("🇬🇷 Greek", callback_data='lang_el')
        ],
        [
            InlineKeyboardButton("🇮🇱 Hebrew", callback_data='lang_he'),
            InlineKeyboardButton("🇭🇺 Hungarian", callback_data='lang_hu'),
            InlineKeyboardButton("🇨🇿 Czech", callback_data='lang_cs')
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data='main_menu')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with language selection"""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user language to English if not set
    if user_id not in user_languages:
        user_languages[user_id] = 'en'
    
    welcome_text = (
        f"👋 **Hello {user.first_name}!**\n\n"
        "Welcome to **Language66 Translator Bot** 🌍\n\n"
        "I can translate any text into your preferred language.\n\n"
        "📌 **How to use:**\n"
        "1️⃣ Select your target language below\n"
        "2️⃣ Send me any text message\n"
        "3️⃣ I'll translate it instantly!\n\n"
        "📋 **Commands:**\n"
        "/start - Show this menu\n"
        "/help - Show help\n"
        "/setlang - Change language\n"
        "/lang - Show current language\n"
        "/reset - Reset to English\n\n"
        f"🌐 **Current language:** {get_language_name(get_user_language(user_id))}"
    )
    
    keyboard = create_language_keyboard()
    await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = (
        "🆘 **Help & Commands**\n\n"
        "🤖 **Bot Features:**\n"
        "• Translate text to 25+ languages\n"
        "• Simple inline keyboard selection\n"
        "• Automatic language detection\n"
        "• Remembers your preference\n\n"
        "📌 **Commands:**\n"
        "/start - Show main menu\n"
        "/help - Show this help\n"
        "/setlang - Change language\n"
        "/lang - Show current language\n"
        "/reset - Reset to English\n\n"
        "💡 **Quick Tip:**\n"
        "Just send any text and I'll translate it automatically!\n\n"
        "🌍 **Supported Languages:**\n"
        "English, Spanish, French, German, Italian,\n"
        "Portuguese, Russian, Chinese, Japanese,\n"
        "Arabic, Hindi, Korean, Dutch, Polish,\n"
        "Turkish, Vietnamese, Thai, Indonesian,\n"
        "Malay, Swahili, Greek, Hebrew, Hungarian, Czech"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection menu"""
    keyboard = create_language_keyboard()
    await update.message.reply_text(
        "🌍 **Choose your target language:**\n"
        "Select from the options below:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def show_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current language"""
    user_id = update.effective_user.id
    lang_code = get_user_language(user_id)
    lang_name = get_language_name(lang_code)
    
    await update.message.reply_text(
        f"🌐 **Your current language:** {lang_name}\n"
        f"📝 **Language code:** `{lang_code}`\n\n"
        "To change it, use /setlang",
        parse_mode='Markdown'
    )

async def reset_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user's language to English"""
    user_id = update.effective_user.id
    user_languages[user_id] = 'en'
    
    await update.message.reply_text(
        "✅ **Language reset to English!**\n"
        "All translations will now be to English.",
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data.startswith('lang_'):
        # Set user's language
        lang_code = data.replace('lang_', '')
        if lang_code in SUPPORTED_LANGUAGES:
            user_languages[user_id] = lang_code
            lang_name = get_language_name(lang_code)
            
            await query.edit_message_text(
                f"✅ **Language set to: {lang_name}**\n\n"
                f"🌍 Now send me any text and I'll translate it to {lang_name}!",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Sorry, this language is not supported yet.")
    
    elif data == 'more_languages':
        # Show more languages
        keyboard = create_more_languages_keyboard()
        await query.edit_message_text(
            "🌍 **Additional Languages:**\n"
            "Select your language from the options below:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    elif data == 'main_menu':
        # Return to main menu
        keyboard = create_language_keyboard()
        current_lang = get_language_name(get_user_language(user_id))
        await query.edit_message_text(
            f"🌍 **Main Menu**\n\n"
            f"🌐 Current language: {current_lang}\n\n"
            "Select a language or send me text to translate!",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate incoming text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Ignore if text is too short or empty
    if not text or len(text.strip()) < 2:
        return
    
    # Get user's target language
    target_lang = get_user_language(user_id)
    target_name = get_language_name(target_lang)
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Translate the text
        translator = GoogleTranslator(target=target_lang)
        translated = translator.translate(text)
        
        # Detect source language (if possible)
        try:
            source_lang = translator.source
            source_name = get_language_name(source_lang)
        except:
            source_name = "Unknown"
        
        # Send translation
        reply_text = (
            f"🌍 **Translation to {target_name}:**\n\n"
            f"{translated}\n\n"
            f"🔄 *From {source_name} → {target_name}*"
        )
        await update.message.reply_text(reply_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Translation error for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ **Translation failed.**\n"
            "Please try again or check if the language is supported.",
            parse_mode='Markdown'
        )

def main():
    """Start the bot"""
    logger.info("🚀 Starting Language66 Translator Bot...")
    
    # Create the Application
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("setlang", set_lang_command))
    app.add_handler(CommandHandler("lang", show_language))
    app.add_handler(CommandHandler("reset", reset_language))
    
    # Add callback query handler for inline keyboards
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Add message handler for translations
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    
    # Start the bot
    logger.info("✅ Bot is ready and running!")
    app.run_polling()

if __name__ == "__main__":
    main()
