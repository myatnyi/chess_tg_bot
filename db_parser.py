import sqlite3
import chess

pieces = {
    0: None,
    1: chess.Pawn('w'), 2: chess.Knight('w'), 3: chess.Rook('w'),
    4: chess.Bishop('w'), 5: chess.Queen('w'), 6: chess.King('w'),
    7: chess.Pawn('b'), 8: chess.Knight('b'), 9: chess.Rook('b'),
    10: chess.Bishop('b'), 11: chess.Queen('b'), 12: chess.King('b'),
}
nums = {'NoneType': 0,
        'Pawnw': 1, 'Knightw': 2, 'Rookw': 3, 'Bishopw': 4, 'Queenw': 5, 'Kingw': 6,
        'Pawnb': 7, 'Knightb': 8, 'Rookb': 9, 'Bishopb': 10, 'Queenb': 11, 'Kingb': 12}


def add_in_stats(id):
    con = sqlite3.connect("dbs/stats.sqlite")
    cur = con.cursor()
    cur.execute(f"INSERT OR IGNORE INTO stats(user_id) VALUES({id})")
    con.commit()
    con.close()


def add_in_queue(id):
    con = sqlite3.connect("dbs/queue.sqlite")
    cur = con.cursor()
    cur.execute(f"INSERT OR IGNORE INTO queue(user_id) VALUES({id})")
    con.commit()
    con.close()


def delete_from_queue(id):
    con = sqlite3.connect("dbs/queue.sqlite")
    cur = con.cursor()
    cur.execute(f"DELETE from queue where user_id = {id}")
    con.commit()
    con.close()


def get_users_from_queue(avoid_id):
    con = sqlite3.connect("dbs/queue.sqlite")
    cur = con.cursor()
    res = cur.execute(f"SELECT user_id FROM queue where user_id != {avoid_id}").fetchall()
    con.commit()
    con.close()
    return res


def create_board(id):
    board = chess.Board().board
    brd = []
    for row in board:
        for el in row:
            brd.append(el)
    brd = ' '.join([str(nums[x.__class__.__name__ + ('' if x.__class__.__name__ == 'NoneType' else x.team)])
                    for x in brd])
    con = sqlite3.connect("dbs/boards.sqlite")
    cur = con.cursor()
    cur.execute(f"INSERT INTO boards(user_id, board) VALUES('{id}', '{brd}')")
    con.commit()
    con.close()


def get_board(id):
    con = sqlite3.connect("dbs/boards.sqlite")
    cur = con.cursor()
    res = cur.execute(f"""SELECT board FROM boards 
    where user_id = '{str(id) + str(get_foe(id))}' or user_id = '{str(get_foe(id)) + str(id)}'""").fetchone()[0].split()
    con.commit()
    con.close()
    res = [pieces[int(x)] for x in res]
    final_res = []
    for i in range(8):
        final_res.append([res[i * 8 + x] for x in range(8)])
    return final_res


def update_board(id, board):
    brd = []
    for row in board:
        for el in row:
            brd.append(el)
    brd = ' '.join([str(nums[x.__class__.__name__ + ('' if x.__class__.__name__ == 'NoneType' else x.team)])
                    for x in brd])
    con = sqlite3.connect("dbs/boards.sqlite")
    cur = con.cursor()
    cur.execute(f"""UPDATE boards SET board = '{brd}' 
    where user_id = '{str(id) + str(get_foe(id))}' or user_id = '{str(get_foe(id)) + str(id)}'""")
    con.commit()
    con.close()


def user_in_game(id):
    con = sqlite3.connect("dbs/boards.sqlite")
    cur = con.cursor()
    res = cur.execute(f"SELECT user_id FROM boards").fetchall()
    res = [x[0] for x in res]
    con.commit()
    con.close()
    id = str(id)
    for i in res:
        if id in (i[:len(i) // 2], i[len(i) // 2:]):
            return True
    return False


def get_foe(id):
    con = sqlite3.connect("dbs/boards.sqlite")
    cur = con.cursor()
    res = cur.execute(f"SELECT user_id FROM boards").fetchall()
    res = [x[0] for x in res]
    con.commit()
    con.close()
    id = str(id)
    for i in res:
        if id in (i[:len(i) // 2], i[len(i) // 2:]):
            return int(i[:len(i) // 2]) if id != i[:len(i) // 2] else int(i[len(i) // 2:])


if __name__ == '__main__':
    print('bepis')
