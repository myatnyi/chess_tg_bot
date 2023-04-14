import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

import chess
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import telebot
from image_board import draw_board
from chess import Piece

BOARD = None
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
    global BOARD
    logging.info('prikol')
    await update.message.reply_text("start_game", reply_markup=markup)
    BOARD = chess.Board()
    return 2
async def game(update, context):
    global BOARD
    message = update.message.text.split()
    if BOARD != None:
        BOARD.move(message[0], message[1])
        await update.message.reply_text('aaaa')
        return 2
    else:
        await update.message.reply_text('bbbb')
#async def rating(update, context):
    #await update.message.reply_text("rating", reply_markup=markup)
    #return 1

async def bye(update, context):
    global reply_keyboard, markup
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text("bye", reply_markup=markup)
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', hello)],
    states={
        1: [CommandHandler('start_game', start_game)],
        2: [MessageHandler(filters.TEXT, game)]
    },
    fallbacks=[CommandHandler('bye', bye)]
)

async def any_massage(update, context):
    if update.message.text != '/rating' and update.message.text != '/start' and update.message.text != '/start_game' and update.message.text != '/bye' and len(update.message.text.split()) != 2:
            await update.message.reply_text("hz")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT, any_massage)
    application.add_handler(CommandHandler("start", hello))
    #application.add_handler(CommandHandler("start_game", start_game))
    #application.add_handler(CommandHandler("rating", rating))
    #application.add_handler(CommandHandler("bye", bye))
    application.add_handler(text_handler)
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()