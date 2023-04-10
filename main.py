import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import telebot

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/start']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

async def hello(update, context):
    global reply_keyboard, markup
    reply_keyboard = [['/start_game'], ['/rating', '/bye']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text('приветик(приветик)', reply_markup=markup)
    return 1


async def start_game(update, context):
    await update.message.reply_text("start_game", reply_markup=markup)
    return 2

async def rating(update, context):
    await update.message.reply_text("rating", reply_markup=markup)
    return 3

async def bye(update, context):
    global reply_keyboard, markup
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text("bye", reply_markup=markup)
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', hello)],
    states={
        1: [MessageHandler(filters.Regex("start_game"), start_game)],
        2: [MessageHandler(filters.Regex("rating"), rating)]
    },
    fallbacks=[CommandHandler('bye', bye)]
)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", hello))
    application.add_handler(CommandHandler("start_game", start_game))
    application.add_handler(CommandHandler("rating", rating))
    application.add_handler(CommandHandler("bye", bye))
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()