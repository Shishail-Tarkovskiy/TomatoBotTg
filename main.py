from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Команда /start для приветствия
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне фотографию, и я отвечу на неё!")

# Обработка фотографий
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отправляем сообщение в ответ на фото
    await update.message.reply_text("Спасибо за фото!")

# Обработка текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправьте фотографию!")

def main():
    # Вставьте сюда токен вашего бота
    BOT_TOKEN = "7223315998:AAGryp3B4y9OoADvPZZAZXCEFPm2wv84JlY"

    # Создание приложения Telegram
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
