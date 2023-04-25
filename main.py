import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
import db_parser
import chess
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import telebot
from image_board import draw_board
import os
import pathlib


bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

start_reply_keyboard = [['/start']]
hub_reply_keyboard = [['/find_game', '/rating'], ['/help', '/bye']]
quit_reply_keyboard = [['/quit']]
markup = ReplyKeyboardMarkup(start_reply_keyboard, one_time_keyboard=False)


value_of_pieces = {'NoneType': 0,
                   'Pawn': 1,
                   'Knight': 2,
                   'Rook': 3,
                   'Bishop': 4,
                   'Queen': 5,
                   'King': 6}


def count_results(id):
    board = db_parser.get_board(id)
    res = 0
    for x in range(len(board)):
        for y in range(len(board[0])):
            res += value_of_pieces[board[x][y].__class__.__name__]
    return res


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
                await update.message.reply_photo(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                              'data', 'result.png'),
                                                 caption=f'*{move_chess}*',
                                                 parse_mode='MarkdownV2')
            else:
                check_kings = BOARD.check_kings()
                await update.message.reply_photo(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                              'data', 'result.png'),
                                                 caption=f'{message[0]} -> {message[1]}\n{check_kings}')
                await context.bot.send_photo(chat_id=db_parser.get_foe(update.message.chat.id),
                                             photo=open(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                                     'data', 'result.png'), 'rb'),
                                             caption=f'Противник делает: {message[0]} -> {message[1]}\n{check_kings}')
                db_parser.update_board(update.message.chat.id, BOARD.board)
                check_pawns = BOARD.check_pawns()
                if check_pawns == 'w' and db_parser.is_turn(update.message.chat.id)[1] == 0 \
                        or check_pawns == 'b' and db_parser.is_turn(update.message.chat.id)[1] == 1:
                    keyboard = [
                            [InlineKeyboardButton("Конь", callback_data="10")],
                            [InlineKeyboardButton("Ладья", callback_data="11")],
                            [InlineKeyboardButton("Слон", callback_data="12")],
                            [InlineKeyboardButton("Королева", callback_data="13")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("На какую фигуру вы хотите поменять пешку?",
                                                    reply_markup=reply_markup)
                else:
                    db_parser.change_turn(update.message.chat.id)
                check_mate = BOARD.check_mate()
                if check_mate:
                    if BOARD.board[check_mate[0][0]][check_mate[0][1]].team == 'w' \
                            and db_parser.is_turn(update.message.chat.id) == 1 \
                            or BOARD.board[check_mate[0][0]][check_mate[0][1]].team == 'b' \
                            and db_parser.is_turn(update.message.chat.id) == 0:
                        res = count_results(update.message.chat.id)
                        db_parser.change_rating(update.message.chat.id, res)
                        db_parser.change_rating(db_parser.get_foe(update.message.chat.id), -res)
                        markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
                        await update.message.reply_text(f'мат\. конгратс\.\n*\+{res} очков рейтинга*',
                                                        reply_markup=markup,
                                                        parse_mode='MarkdownV2')
                        await context.bot.send_message(chat_id=db_parser.get_foe(update.message.chat.id),
                                                       text=f'мат\. увы\.\n*\-{res} очков рейтинга*',
                                                       reply_markup=markup,
                                                       parse_mode='MarkdownV2')
                        db_parser.close_game(update.message.chat.id)
                    else:
                        res = count_results(update.message.chat.id)
                        db_parser.change_rating(update.message.chat.id, -res)
                        db_parser.change_rating(db_parser.get_foe(update.message.chat.id), res)
                        markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
                        keyboard = [[InlineKeyboardButton("Ок", callback_data="5")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(f'мат\. увы\.\n*\-{res} очков рейтинга*',
                                                        reply_markup=markup,
                                                        parse_mode='MarkdownV2')
                        await context.bot.send_message(chat_id=db_parser.get_foe(update.message.chat.id),
                                                       text=f'мат\. конгратс\.\n*\+{res} очков рейтинга*',
                                                       reply_markup=reply_markup,
                                                       parse_mode='MarkdownV2')
                        db_parser.close_game(update.message.chat.id)
                    return 1
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
            await update.message.reply_text(f'игра найдена подключаюсь к *{bot.get_chat(foe_user).first_name}*\n'
                                            f'вы играете за белых',
                                            reply_markup=markup, parse_mode='MarkdownV2')
            await context.bot.send_message(chat_id=foe_user,
                                           text=f'игра найдена подключаюсь к *{update.message.chat.first_name}*\n'
                                                f'вы играете за черных',
                                           reply_markup=markup, parse_mode='MarkdownV2')
            BOARD = chess.Board()
            BOARD.board = db_parser.get_board(update.message.chat.id)
            draw_board(BOARD.board)
            await update.message.reply_photo(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                          'data', 'result.png'))
            await context.bot.send_photo(chat_id=db_parser.get_foe(update.message.chat.id),
                                         photo=open(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                                 'data', 'result.png'), 'rb'))
        else:
            db_parser.add_in_queue(update.message.chat.id)
    return 2


async def rating(update, context):
    need_message = db_parser.get_rating(update.message.chat.id)
    markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
    top_10 = [(f'*{bot.get_chat(x[0]).first_name} \- {x[1]} *' if need_message[1][0] == x[0] else
               f'{bot.get_chat(x[0]).first_name} \- {x[1]}') for x in sorted(need_message[0], key=lambda x: x[1])]
    top_10 = '\n'.join(top_10)
    await update.message.reply_text(f"общий рейтинг:\n{top_10} \n\n"
                                    f"Ваш рейтинг: {need_message[1][1]}", reply_markup=markup, parse_mode='MarkdownV2')
    return 1


async def bye(update, context):
    markup = ReplyKeyboardMarkup(start_reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text("bye", reply_markup=markup)
    return ConversationHandler.END


async def quit(update, context):
    if db_parser.user_in_game(update.message.chat.id):
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data="1"),
                InlineKeyboardButton("Нет", callback_data="2")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Уверены что хотите сдаться и выйти?", reply_markup=reply_markup)
    else:
        markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
        db_parser.delete_from_queue(update.message.chat.id)
        await update.message.reply_text('выхожу из очереди', reply_markup=markup)
        return 1


async def button(update, context):
    query = update.callback_query
    await query.answer()
    match query.data:
        case '1':
            res = count_results(query.from_user.id)
            db_parser.change_rating(query.from_user.id, -res)
            db_parser.change_rating(db_parser.get_foe(query.from_user.id), res)
            markup = ReplyKeyboardMarkup(hub_reply_keyboard, one_time_keyboard=False)
            await context.bot.send_message(chat_id=query.from_user.id,
                                           text=f'вы сдались увы\n*\-{res} очков рейтинга*',
                                           reply_markup=markup,
                                           parse_mode='MarkdownV2')
            keyboard = [[InlineKeyboardButton("Ок", callback_data="5")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=db_parser.get_foe(query.from_user.id),
                                           text=f'ваш противник сдался\n*\+{res} очков рейтинга*',
                                           reply_markup=reply_markup,
                                           parse_mode='MarkdownV2')
            db_parser.close_game(query.from_user.id)
            return 1
        case '2':
            await query.edit_message_text(text=f"👍")
            return 2
        case '5':
            await query.edit_message_text(text=f"👍")
            return 1
        case '10':
            BOARD = chess.Board()
            BOARD.board = db_parser.get_board(query.from_user.id)
            check_pawns = BOARD.check_pawns()
            BOARD.change_pawn(chess.Knight(check_pawns), check_pawns)
            db_parser.update_board(query.from_user.id, BOARD.board)
            db_parser.change_turn(update.message.chat.id)
            await context.bot.send_message(chat_id=db_parser.get_foe(query.from_user.id),
                                           text=f'противник поменял свою пешку на коня')
            await query.edit_message_text(text=f"♟️")
            return 2
        case '11':
            BOARD = chess.Board()
            BOARD.board = db_parser.get_board(query.from_user.id)
            check_pawns = BOARD.check_pawns()
            BOARD.change_pawn(chess.Rook(check_pawns), check_pawns)
            db_parser.update_board(query.from_user.id, BOARD.board)
            db_parser.change_turn(query.from_user.id)
            await context.bot.send_message(chat_id=db_parser.get_foe(query.from_user.id),
                                           text=f'противник поменял свою пешку на ладью')
            await query.edit_message_text(text=f"♟️")
            return 2
        case '12':
            BOARD = chess.Board()
            BOARD.board = db_parser.get_board(query.from_user.id)
            check_pawns = BOARD.check_pawns()
            BOARD.change_pawn(chess.Bishop(check_pawns), check_pawns)
            db_parser.update_board(query.from_user.id, BOARD.board)
            db_parser.change_turn(query.from_user.id)
            await context.bot.send_message(chat_id=db_parser.get_foe(query.from_user.id),
                                           text=f'противник поменял свою пешку на слона')
            await query.edit_message_text(text=f"♟️")
            return 2
        case '13':
            BOARD = chess.Board()
            BOARD.board = db_parser.get_board(query.from_user.id)
            check_pawns = BOARD.check_pawns()
            BOARD.change_pawn(chess.Queen(check_pawns), check_pawns)
            db_parser.update_board(query.from_user.id, BOARD.board)
            db_parser.change_turn(query.from_user.id)
            await context.bot.send_message(chat_id=db_parser.get_foe(query.from_user.id),
                                           text=f'противник поменял свою пешку на королеву')
            await query.edit_message_text(text=f"♟️")
            return 2


async def help(update, context):
    await update.message.reply_text("""хелп
    /find_game - найти игру
    /rating - показать рейтинг ваш и других игроков
    /bye - пока""")
    return 1


async def game_help(update, context):
    await update.message.reply_text('ход пишется типа "H6 F6"\n'
                                    'не знаете правила? вам сюда - en.wikipedia.org/wiki/Rules_of_chess')


async def default_ans(update, context):
    await update.message.reply_text('/help для хелп')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', hello)],
        states={
            1: [CommandHandler('find_game', find_game), CommandHandler('rating', rating), CommandHandler('help', help),
                MessageHandler(filters.TEXT & ~filters.COMMAND, default_ans)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_game), CommandHandler('quit', quit),
                CommandHandler('help', game_help), CallbackQueryHandler(button)]
        },
        fallbacks=[CommandHandler('bye', bye)]
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
