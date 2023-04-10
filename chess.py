class Board:
    def __init__(self):
        self.board = []
        for row in range(8):
            self.board.append([None] * 8)
        self.board[7] = [
            Rook('w'), Knight('w'), Bishop('w'), Queen('w'),
            King('w'), Bishop('w'), Knight('w'), Rook('w')
        ]
        self.board[6] = [
            Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w'),
            Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w')
        ]
        self.board[1] = [
            Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'),
            Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b')
        ]
        self.board[0] = [
            Rook('b'), Knight('b'), Bishop('b'), Queen('b'),
            King('b'), Bishop('b'), Knight('b'), Rook('b')
        ]

    def move(self, pos1, pos2):
        litterals = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
        if len(pos1) == 2 and len(pos2) == 2 and pos1[1].isdigit() and pos2[1].isdigit():
            if pos1[0] in litterals.keys() and pos2[0] in litterals.keys() \
                    and int(pos1[1]) in range(1, 9) and int(pos2[1]) in range(1, 9):
                new_pos1 = (8 - int(pos1[1]), litterals[pos1[0]])
                new_pos2 = (8 - int(pos2[1]), litterals[pos2[0]])
                if self.board[new_pos1[0]][new_pos1[1]]:
                    if self.board[new_pos1[0]][new_pos1[1]].move_to(self.board, new_pos1, new_pos2) == 0:
                        self.board[new_pos2[0]][new_pos2[1]] = self.board[new_pos1[0]][new_pos1[1]]
                        self.board[new_pos1[0]][new_pos1[1]] = None
                        return 0
                return self.board[new_pos1[0]][new_pos1[1]].move_to(self.board, new_pos1, new_pos2)
        return 'хдд'


class Piece:
    def __init__(self, team):
        self.team = team

    def general_check(self, board, pos1, pos2):
        if pos1 == pos2:
            return 'сейм координатс'
        if board[pos2[0]][pos2[1]]:
            if board[pos2[0]][pos2[1]].team == self.team:
                return 'там уже стоит союзник'
        return 0


class Pawn(Piece):
    def __init__(self, team):
        super().__init__(team)

    def move_to(self, board, pos1, pos2):
        if self.general_check(board, pos1, pos2):
            return self.general_check(board, pos1, pos2)
        if (self.team == 'w' and pos1[0] - pos2[0] == 1) or (self.team == 'b' and pos2[0] - pos1[0] == 1):
            if board[pos2[0]][pos2[1]] and abs(pos2[1] - pos1[1]) == 1:
                return 0
            elif (not board[pos2[0]][pos2[1]]) and pos2[1] - pos1[1] == 0:
                return 0
        return 'пешки не могут так ходить'


class Rook(Piece):
    def __init__(self, team):
        super().__init__(team)

    def move_to(self, board, pos1, pos2):
        if self.general_check(board, pos1, pos2):
            return self.general_check(board, pos1, pos2)
        if pos2[0] == pos1[0] and pos2[1] != pos2[0] or pos2[0] != pos1[0] and pos2[1] == pos2[0]:
            if pos2[0] == pos1[0]:
                if any([board[pos1[0] + i * ((pos2[0] - pos1[0]) / abs(pos2[0] - pos1[0]))][pos1[1]]
                        for i in range(abs(pos2[0] - pos1[0]))]):
                    return 'ладьи так не ходят........'
            elif pos2[1] == pos1[1]:
                if any([board[pos1[0]][pos1[1] + i * ((pos2[1] - pos1[1]) / abs(pos2[1] - pos1[1]))]
                        for i in range(abs(pos2[1] - pos1[1]))]):
                    return 'ладьи так не ходят........'
            return 0
        return pos2[1] == pos2[0]


class Knight(Piece):
    def __init__(self, team):
        super().__init__(team)

    def move_to(self, board, pos1, pos2):
        if self.general_check(board, pos1, pos2):
            return self.general_check(board, pos1, pos2)
        if [abs(pos2[0] - pos1[0]), abs(pos2[1] - pos1[1])] in [[1, 2], [2, 1]]:
            return 0
        return 'кони так не ходят'


class Bishop(Piece):
    def __init__(self, team):
        super().__init__(team)

    def move_to(self, board, pos1, pos2):
        if self.general_check(board, pos1, pos2):
            return self.general_check(board, pos1, pos2)
        if abs(pos2[0] - pos1[0]) == abs(pos2[1] - pos1[0]):
            if any([board[pos1[0] + i * ((pos2[0] - pos1[0]) / abs(pos2[0] - pos1[0]))]
                    [pos1[1] + i * ((pos2[1] - pos1[1]) / abs(pos2[1] - pos1[1]))]
                    for i in range(abs(pos2[0] - pos1[0]))]):
                return 'увы слоны так не ходят к сожалению и несчастью'
        return 0


class Queen(Piece):
    def __init__(self, team):
        super().__init__(team)

    def move_to(self, board, pos1, pos2):
        if self.general_check(board, pos1, pos2):
            return self.general_check(board, pos1, pos2)
        if abs(pos2[0] - pos1[0]) == abs(pos2[1] - pos1[0]):
            if not any([board[pos1[0] + i * ((pos2[0] - pos1[0]) / abs(pos2[0] - pos1[0]))]
                        [pos1[1] + i * ((pos2[1] - pos1[1]) / abs(pos2[1] - pos1[1]))]
                        for i in range(abs(pos2[0] - pos1[0]))]):
                return 0
        if pos2[0] == pos1[0] and pos2[1] != pos2[0] or pos2[0] != pos1[0] and pos2[1] == pos2[0]:
            if pos2[0] == pos1[0]:
                if not any([board[pos1[0] + i * ((pos2[0] - pos1[0]) / abs(pos2[0] - pos1[0]))][pos1[1]]
                            for i in range(abs(pos2[0] - pos1[0]))]):
                    return 0
            if pos2[1] == pos1[1]:
                if not any([board[pos1[0]][pos1[1] + i * ((pos2[1] - pos1[1]) / abs(pos2[1] - pos1[1]))]
                            for i in range(abs(pos2[1] - pos1[1]))]):
                    return 0
        return 'настоящие квины так бы не поступили'


class King(Piece):
    def __init__(self, team):
        super().__init__(team)

    def move_to(self, board, pos1, pos2):
        if self.general_check(board, pos1, pos2):
            return self.general_check(board, pos1, pos2)
        if abs(pos2[0] - pos1[0]) in [0, 1] and abs(pos2[1] - pos1[1]) in [0, 1] \
                and self.is_in_danger(board, pos2) == 0:
            return 0
        return 'абсолютно не мудрое решение со стороны короля'

    def is_in_danger(self, board, pos):
        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] and board[y][x].team != self.team:
                    if board[y][x].move_to(board, (y, x), pos) == 0:
                        return 'король в опасности'
        return 0
