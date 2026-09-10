import os

# Конфигурация бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")
# Базовый адрес Telegram API (можно указать зеркало)
PROXY_URL = os.getenv("PROXY_URL", "https://api.telegram.org")
DB_NAME = 'quiz_bot.db'
