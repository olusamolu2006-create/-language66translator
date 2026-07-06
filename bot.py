import os
import logging
import re
from typing import Dict, Optional
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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("❌ No bot token found. Set TELEGRAM_BOT_TOKEN environment variable.")
    exit(1)

# Available languages with their codes and names
SUPPORTED_LANGUAGES = {
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'am': 'Amharic',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'co': 'Corsican',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek',
    'gu': 'Gujarati',
    'ht': 'Haitian Creole',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'iw': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'ig': 'Igbo',
    'id': 'Indonesian',
    'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jv': 'Javanese',
    'kn': 'Kannada',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'rw': 'Kinyarwanda',
    'ko': 'Korean',
    'ku': 'Kurdish',
    'ky': 'Kyrgyz',
    'lo': 'Lao',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian',
    'mg': 'Malagasy',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'ny': 'Nyanja (Chichewa)',
    'or': 'Odia (Oriya)',
    'ps': 'Pashto',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pa': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'sn': 'Shona',
    'sd': 'Sindhi',
    'si': 'Sinhala (Sinhalese)',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'es': 'Spanish',
    'su': 'Sundanese',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tl': 'Tagalog (Filipino)',
    'tg': 'Tajik',
    'ta': 'Tamil',
    'tt': 'Tatar',
    'te': 'Telugu',
    'th': 'Thai',
    'tr': 'Turkish',
    'tk': 'Turkmen',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'ug': 'Uyghur',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu'
}

# --- User Data Management ---
# In-memory storage for user preferences
# For production, consider using a database like PostgreSQL
user_data: Dict[int, Dict] = {}

def get_user_language(user_id: int) -> str:
    """Get the user's preferred target language, defaulting to English."""
    return user_data.get(user_id, {}).get('target_lang', 'en')

def set_user_language(user_id: int, language_code: str) -> None:
    """Set the user's preferred target language."""
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['target_lang'] = language_code

def get_user_name(user_id: int) -> str:
    """Get the user's preferred name."""
    return user_data.get(user_id, {}).get('name', 'User')

def set_user_name(user_id: int, name: str) -> None:
    """Set the user's preferred name."""
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['name'] = name

# --- Helper Functions ---
def get_language_name(code: str) -> str:
    """Get the full language name from its code."""
    return SUPPORTED_LANGUAGES.get(code, code)

def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard with popular languages."""
    popular_codes = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh-CN', 'ja', 'ar', 'hi', 'ko']
    keyboard = []
    row = []
    for i, code in enumerate(popular_codes):
        name = get_language_name(code)
        row.append(InlineKeyboardButton(name, callback_data=f'setlang_{code}'))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🌍 More Languages", callback_data="more_langs")])
    return InlineKeyboardMarkup(keyboard)

def create_full_language_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Create a paginated keyboard with all languages."""
    codes = list(SUPPORTED_LANGUAGES.keys())
    items_per_page = 20
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(codes))
    
    keyboard = []
    for code in codes[start_idx:end_idx]:
        name = get_language_name(code)
        keyboard.append([InlineKeyboardButton(f"{name} ({code})", callback_data=f'setlang_{code}')])
    
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f'page_{page-1}'))
    if end_idx < len(codes):
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f'page_{page+1}'))
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Popular", callback_data="popular_langs")])
    return InlineKeyboardMarkup(keyboard)

# --- Bot Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Store user's name
    set_user_name(user_id, user.first_name)
    
    welcome_text = (
        f"👋 **Welcome {user.first_name}!**\n\n"
        "I am the **Language66 Translator Bot** 🌍\n"
        "I can translate your messages into any language you choose.\n\n"
        "🔧 **Commands:**\n"
        "• `/start` - Show this welcome message\n"
        "• `/help` - Show help and available languages\n"
        "• `/setlang` - Choose your target language (with keyboard)\n"
        "• `/lang` - Show your current target language\n"
        "• `/reset` - Reset your language to English\n"
        "• `/about` - About this bot\n\n"
        "💡 **How to use:**\n"
        "Simply send me any text, and I will translate it to your chosen language!\n\n"
        "Your current language is: **English** (Default)"
    )
    
    keyboard = create_language_keyboard()
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a list of available commands and languages."""
    help_text = (
        "🆘 **Help Menu**\n\n"
        "📌 **Commands:**\n"
        "• `/start` - Show welcome message\n"
        "• `/help` - Show this help menu\n"
        "• `/setlang` - Choose your target language\n"
        "• `/lang` - Show your current target language\n"
        "• `/reset` - Reset language to English\n"
        "• `/about` - About this bot\n\n"
        "🌐 **How Translation Works:**\n"
        "1. Set your target language using `/setlang`\n"
        "2. Send any text message\n"
        "3. The bot will automatically translate it!\n\n"
        "🔤 **Popular Languages:**\n"
        "English (en), Spanish (es), French (fr),\n"
        "German (de), Italian (it), Portuguese (pt),\n"
        "Russian (ru), Chinese (zh-CN), Japanese (ja),\n"
        "Arabic (ar), Hindi (hi), Korean (ko)\n\n"
        "For a complete list, use the keyboard in `/setlang`"
    )
    await update.message.reply_text(help_text)

async def set_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection keyboard."""
    keyboard = create_language_keyboard()
    await update.message.reply_text(
        "🌍 **Choose your target language:**\n"
        "Select from the popular languages below, or click 'More Languages' for a complete list.",
        reply_markup=keyboard
    )

async def show_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the user's current target language."""
    user_id = update.effective_user.id
    language_code = get_user_language(user_id)
    language_name = get_language_name(language_code)
    
    await update.message.reply_text(
        f"🌍 Your current target language is **{language_name}** (`{language_code}`).\n\n"
        "To change it, use the `/setlang` command."
    )

async def reset_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset the user's language to English."""
    user_id = update.effective_user.id
    set_user_language(user_id, 'en')
    await update.message.reply_text(
        "✅ Your language has been reset to **English**.\n"
        "All translations will now be to English."
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show information about the bot."""
    about_text = (
        "🤖 **About Language66 Translator Bot**\n\n"
        "Version: 1.0.0\n"
        "Developer: @YourUsername\n"
        "Powered by: Google Translate API\n\n"
        "🌐 Supports translation to 100+ languages\n"
        "🔒 Privacy-focused: No messages are stored\n"
        "⚡ Fast and reliable translations\n\n"
        "📱 Built with:\n"
        "• Python 3.9+\n"
        "• python-telegram-bot library\n"
        "• deep-translator library\n"
        "• Deployed on Railway 🚀\n\n"
        "💡 For feedback or issues, contact the developer."
    )
    await update.message.reply_text(about_text)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data.startswith('setlang_'):
        language_code = data.replace('setlang_', '')
        if language_code in SUPPORTED_LANGUAGES:
            set_user_language(user_id, language_code)
            language_name = get_language_name(language_code)
            await query.edit_message_text(
                f"✅ Your target language has been set to **{language_name}** (`{language_code}`).\n\n"
                "Now send me any text, and I'll translate it for you! 🌍"
            )
        else:
            await query.edit_message_text("❌ Sorry, this language is not supported.")
    
    elif data == "more_langs":
        keyboard = create_full_language_keyboard(0)
        await query.edit_message_text(
            "🌍 **All Available Languages:**\n"
            "Select your target language from the list below:",
            reply_markup=keyboard
        )
    
    elif data == "popular_langs":
        keyboard = create_language_keyboard()
        await query.edit_message_text(
            "🌍 **Choose your target language:**\n"
            "Select from the popular languages below:",
            reply_markup=keyboard
        )
    
    elif data.startswith('page_'):
        page = int(data.replace('page_', ''))
        keyboard = create_full_language_keyboard(page)
        await query.edit_message_text(
            "🌍 **All Available Languages:**\n"
            f"Page {page + 1}",
            reply_markup=keyboard
        )

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Translate the user's incoming text message to their target language.
    This function is triggered for all text messages that are not commands.
    """
    user_id = update.effective_user.id
    text_to_translate = update.message.text
    
    if not text_to_translate:
        return
    
    # Ignore very short messages
    if len(text_to_translate.strip()) < 2:
        return
    
    target_lang = get_user_language(user_id)
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Use deep-translator to translate the text
        translator = GoogleTranslator(target=target_lang)
        translated_text = translator.translate(text_to_translate)
        
        # Detect source language (if possible)
        try:
            source_lang = translator.source
            source_lang_name = get_language_name(source_lang)
        except:
            source_lang_name = "Unknown"
        
        target_lang_name = get_language_name(target_lang)
        
        # Send the translation back to the user
        reply_text = (
            f"📝 **Translation**\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"{translated_text}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🔄 *From {source_lang_name} → {target_lang_name}*"
        )
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"Translation error for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't translate that text.\n"
            "Please make sure the language is supported and try again."
        )

# --- Main Function ---

def main():
    """Start the bot."""
    logger.info("🚀 Starting Language66 Translator Bot...")
    
    # Create the Application
    application = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setlang", set_language_command))
    application.add_handler(CommandHandler("lang", show_language))
    application.add_handler(CommandHandler("reset", reset_language))
    application.add_handler(CommandHandler("about", about_command))
    
    # Add callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Add a handler for all other text messages (non-commands)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message)
    )

    # Start the bot using long polling
    logger.info("✅ Bot is running and ready to translate!")
    application.run_polling()

if __name__ == "__main__":
    main()
