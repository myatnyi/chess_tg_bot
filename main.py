import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
import db_parser
import chess
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import telebot
from image_board import draw_board


bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

start_reply_keyboard = [['/start']]
hub_reply_keyboard = [['/find_game', '/rating'], ['/help', '/bye']]
quit_reply_keyboard = [['/quit']]
markup = ReplyKeyboardMarkup(start_reply_keyboard, one_time_keyboard=False)


async def hello(update, context):
    markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
    db_parser.add_in_stats(update.message.chat.id)
    await update.message.reply_text('приветик(приветик)', reply_markup=markup)
    return 1


async def find_game(update, context):
    if db_parser.user_in_game(update.message.chat.id):
        BOARD = chess.Board()
        BOARD.board = db_parser.get_board(update.message.chat.id)
        if db_parser.is_turn(update.message.chat.id)[0]:
            message = update.message.text.split()
            move_chess = BOARD.move(message[0], message[1], db_parser.is_turn(update.message.chat.id)[1])
            draw_board(BOARD.board)
            if move_chess:
                await update.message.reply_photo('data/result.png',
                                                 caption=f'**{move_chess}**',
                                                 parse_mode='MarkdownV2')
            else:
                check_kings = BOARD.check_kings()
                await update.message.reply_photo('data/result.png',
                                                 caption=f'{message[0]} -> {message[1]}\n{check_kings}')
                await context.bot.send_photo(chat_id=db_parser.get_foe(update.message.chat.id),
                                             photo=open('data/result.png', 'rb'),
                                             caption=f'Противник делает: {message[0]} -> {message[1]}\n{check_kings}')
                db_parser.update_board(update.message.chat.id, BOARD.board)
                db_parser.change_turn(update.message.chat.id)
        else:
            await update.message.reply_text('не твой ход жди пока противник походит')
    else:
        markup = ReplyKeyboardMarkup(quit_reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text("ищу игру", reply_markup=markup)
        queue_users = db_parser.get_users_from_queue(update.message.chat.id)
        if queue_users:
            foe_user = queue_users[0][0]
            db_parser.delete_from_queue(foe_user)
            db_parser.create_board(int(str(update.message.chat.id) + str(foe_user)))
            await update.message.reply_text(f'игра найдена подключаюсь к {bot.get_chat(foe_user).first_name}\n'
                                            f'вы играете за белых',
                                            reply_markup=markup, parse_mode='MarkdownV2')
            await context.bot.send_message(chat_id=foe_user,
                                           text=f'игра найдена подключаюсь к {update.message.chat.first_name}\n'
                                                f'вы играете за черных',
                                           reply_markup=markup, parse_mode='MarkdownV2')
            BOARD = chess.Board()
            BOARD.board = db_parser.get_board(update.message.chat.id)
            draw_board(BOARD.board)
            await update.message.reply_photo('data/result.png')
            await context.bot.send_photo(chat_id=db_parser.get_foe(update.message.chat.id),
                                         photo=open('data/result.png', 'rb'))
        else:
            db_parser.add_in_queue(update.message.chat.id)
    return 2


async def rating(update, context):
    need_message = db_parser.get_rating(update.message.chat.id)
    await update.message.reply_text(f"общий рейтинг:{need_message[0]}\n"
                                    f"Ваш рейтинг:{need_message[1]}", reply_markup=markup)
    return 1


async def bye(update, context):
    markup = ReplyKeyboardMarkup(start_reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text("bye", reply_markup=markup)
    return ConversationHandler.END


async def quit(update, context):
    markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
    db_parser.delete_from_queue(update.message.chat.id)
    await update.message.reply_text('выхожу из очереди', reply_markup=markup)
    return 1


async def help(update, context):
    await update.message.reply_text("""хелп
    /find_game - найти игру
    /rating - показать рейтинг ваш и других игроков
    /bye - пока""")
    return 1


async def default_ans(update, context):
    await update.message.reply_text('/help для хелп')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', hello)],
        states={
            1: [CommandHandler('find_game', find_game), CommandHandler('rating', rating), CommandHandler('help', help),
                MessageHandler(filters.TEXT & ~filters.COMMAND, default_ans)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_game), CommandHandler('quit', quit)]
        },
        fallbacks=[CommandHandler('bye', bye)]
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
