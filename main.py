import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup
import telebot

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/hello', '/start'],
                  ['/rating', '/bye']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
async def hello(update, context):
    await update.message.reply_text('приветик(приветик)', reply_markup=markup)


async def start_game(update, context):
    await update.message.reply_text("start", reply_markup=markup)


async def rating(update, context):
    await update.message.reply_text("rating", reply_markup=markup)


async def bye(update, context):
    await update.message.reply_text("bye", reply_markup=markup)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("start", start_game))
    application.add_handler(CommandHandler("rating", rating))
    application.add_handler(CommandHandler("bye", bye))
    text_handler = MessageHandler(filters.TEXT, hello)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
