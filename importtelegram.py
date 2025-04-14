import telegram
import asyncio

async def delete_webhook():
    bot_token = '7503926130:AAHLSjE9pDUeI-FUNvs_azJSYhulUAz-p5c'  # замените на ваш токен
    bot = telegram.Bot(token=bot_token)
    
    # Удаляем старый вебхук, если он был настроен
    await bot.delete_webhook()
    print("Вебхук удален!")

# Запуск асинхронной функции
asyncio.run(delete_webhook())
