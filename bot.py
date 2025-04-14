import logging
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Читаем токены
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настроим OpenAI API
openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для начала работы с ботом
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Образование и саморазвитие", callback_data='education')],
        [InlineKeyboardButton("Подготовка к собеседованиям", callback_data='interview')],
        [InlineKeyboardButton("Конструктор резюме", callback_data='resume')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Я твой личный помощник по развитию твоих навыков и продвижению в карьере. '
                              'Выбери одну из категорий:', reply_markup=reply_markup)

# Функция для обработки выбора категории
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  # Отвечаем на запрос

    category = query.data

    if category == 'education':
        question = "Чем я могу помочь в области образования и саморазвития?"
    elif category == 'interview':
        question = "Чем я могу помочь в подготовке к собеседованиям?"
    elif category == 'resume':
        question = "Чем я могу помочь в создании и улучшении резюме?"
    
    # Спрашиваем пользователя
    query.edit_message_text(text=f"Вы выбрали: {question}\nПишите свой вопрос!")

    # Переключаем состояние на открытый диалог
    context.user_data['category'] = category  # Сохраняем выбранную категорию

# Функция для обработки текстовых сообщений и запросов
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    category = context.user_data.get('category', None)

    # Если категория выбрана, обрабатываем запрос
    if category:
        response = get_openai_response(user_message)
        update.message.reply_text(response)
    else:
        update.message.reply_text("Сначала выбери одну из категорий, чтобы начать.")

# Функция для запроса к OpenAI
def get_openai_response(user_message: str) -> str:
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Используем модель GPT-3
            prompt=user_message,
            max_tokens=150,  # Ограничиваем количество слов
            temperature=0.7  # Настроим температуру для разнообразия ответов
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return "Произошла ошибка при обработке запроса."

# Основная функция для запуска бота
def main() -> None:
    # Создаем объект Updater и передаем ему токен бота
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Получаем диспетчер для добавления обработчиков
    dispatcher = updater.dispatcher

    # Обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Обработчик кнопок
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Обработчик текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запускаем бота
    updater.start_polling()

    # Ожидаем завершения работы
    updater.idle()

if __name__ == '__main__':
    main()
