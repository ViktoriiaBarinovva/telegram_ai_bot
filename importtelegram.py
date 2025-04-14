import telegram
import os
import asyncio
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Загрузка токена
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def delete_webhook():
    bot = telegram.Bot(token=BOT_TOKEN)
    
    try:
        # Удаляем старый вебхук, если он был настроен
        await bot.delete_webhook()
        print("Вебхук удален!")
    except Exception as e:
        print(f"Ошибка при удалении вебхука: {e}")

# Запуск асинхронной функции
if __name__ == '__main__':
    asyncio.run(delete_webhook())