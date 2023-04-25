from PIL import Image
import chess
import pathlib
import os
os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'pawn_w.png')


def draw_board(board):
    piece_images_w = {'Pawn': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'pawn_w.png')),
                      'Knight': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                        'data', 'knight_w.png')),
                      'Rook': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'rook_w.png')),
                      'Bishop': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                        'data', 'bishop_w.png')),
                      'Queen': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'queen_w.png')),
                      'King': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'king_w.png'))}
    piece_images_b = {'Pawn': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'pawn_b.png')),
                      'Knight': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                        'data', 'knight_b.png')),
                      'Rook': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'rook_b.png')),
                      'Bishop': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                        'data', 'bishop_b.png')),
                      'Queen': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'queen_b.png')),
                      'King': Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'king_b.png'))}
    board_im = Image.open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'board.png'))
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x]:
                if board[y][x].team == 'w':
                    board_im.paste(piece_images_w[board[y][x].__class__.__name__], (230 + 120 * x, 230 + 120 * y),
                                   piece_images_w[board[y][x].__class__.__name__])
                elif board[y][x].team == 'b':
                    board_im.paste(piece_images_b[board[y][x].__class__.__name__], (230 + 120 * x, 230 + 120 * y),
                                   piece_images_b[board[y][x].__class__.__name__])
    board_im.save(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'result.png'))


if __name__ == '__main__':
    board = chess.Board()
    while True:
        draw_board(board.board)
        pos1, pos2 = input().split()
        print(board.move(pos1, pos2))