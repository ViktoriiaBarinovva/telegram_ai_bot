import logging
import openai
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Пример: https://your-app.onrender.com/webhook
PORT = int(os.environ.get("PORT", 8443))  # Render передаёт порт в переменной PORT

openai.api_key = OPENAI_API_KEY

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Образование и саморазвитие", callback_data='education')],
        [InlineKeyboardButton("Подготовка к собеседованиям", callback_data='interview')],
        [InlineKeyboardButton("Конструктор резюме", callback_data='resume')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Привет! Я твой личный помощник по развитию твоих навыков и продвижению в карьере.\nВыбери одну из категорий:',
        reply_markup=reply_markup
    )

# Обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    category = query.data
    context.user_data['category'] = category

    if category == 'education':
        text = "Вы выбрали: Образование и саморазвитие\nПишите свой вопрос!"
    elif category == 'interview':
        text = "Вы выбрали: Подготовка к собеседованиям\nПишите свой вопрос!"
    elif category == 'resume':
        text = "Вы выбрали: Конструктор резюме\nПишите свой вопрос!"
    else:
        text = "Неверная категория."

    await query.edit_message_text(text=text)

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    category = context.user_data.get('category')

    if category:
        response = await get_openai_response(user_message)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Сначала выбери одну из категорий, чтобы начать.")

# Запрос к OpenAI
async def get_openai_response(user_message: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — полезный помощник по карьерному развитию."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return "Произошла ошибка при обработке запроса. Попробуйте позже."

# Запуск бота с webhook
def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook-запуск с указанием пути
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        webhook_path="/webhook",  # обязательно, иначе Telegram не поймёт путь
    )

if __name__ == '__main__':
    main()
