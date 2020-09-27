import re

INITIAL_STATE = {
    'a8': 'br',
    'b8': 'bn',
    'c8': 'bb',
    'd8': 'bq',
    'e8': 'bk',
    'f8': 'bb',
    'g8': 'bn',
    'h8': 'br',
    'a7': 'bp',
    'b7': 'bp',
    'c7': 'bp',
    'd7': 'bp',
    'e7': 'bp',
    'f7': 'bp',
    'g7': 'bp',
    'h7': 'bp',
    'a6': '',
    'b6': '',
    'c6': '',
    'd6': '',
    'e6': '',
    'f6': '',
    'g6': '',
    'h6': '',
    'a5': '',
    'b5': '',
    'c5': '',
    'd5': '',
    'e5': '',
    'f5': '',
    'g5': '',
    'h5': '',
    'a4': '',
    'b4': '',
    'c4': '',
    'd4': '',
    'e4': '',
    'f4': '',
    'g4': '',
    'h4': '',
    'a3': '',
    'b3': '',
    'c3': '',
    'd3': '',
    'e3': '',
    'f3': '',
    'g3': '',
    'h3': '',
    'a2': 'wp',
    'b2': 'wp',
    'c2': 'wp',
    'd2': 'wp',
    'e2': 'wp',
    'f2': 'wp',
    'g2': 'wp',
    'h2': 'wp',
    'a1': 'wr',
    'b1': 'wn',
    'c1': 'wb',
    'd1': 'wq',
    'e1': 'wk',
    'f1': 'wb',
    'g1': 'wn',
    'h1': 'wr'
}

COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']


class ChessGame:
    def __init__(self, pgn):
        self.moves = []
        self.is_finished = False
        self.is_white_turn = True
        self._last_played_move_index = -1

        self._parse_pgn_file(pgn)
        self.state = INITIAL_STATE.copy()

    def _check_knight_move(self, sqr1, sqr2):
        cd = abs(ord(sqr1[0]) - ord(sqr2[0]))
        rd = abs(int(sqr1[1]) - int(sqr2[1]))
        return (cd == 2 and rd == 1) or (cd == 1 and rd == 2)

    def _check_line(self, sqr1, sqr2):
        c1 = sqr1[0]
        c2 = sqr2[0]
        r1 = int(sqr1[1])
        r2 = int(sqr2[1])
        if r1 == r2:
            i1, i2 = ord(c1) - 97, ord(c2) - 97
            return all(self.state[COLUMNS[i] + str(r1)] == ''
                       for i in range(min(i1, i2) + 1, max(i1, i2)))
        elif c1 == c2:
            return all(self.state[c1 + str(i)] == ''
                       for i in range(min(r1, r2) + 1, max(r1, r2)))
        return False

    def _check_diagonal(self, sqr1, sqr2):
        c1 = ord(sqr1[0]) - 97
        c2 = ord(sqr2[0]) - 97
        r1 = int(sqr1[1])
        r2 = int(sqr2[1])

        if abs(c1 - c2) == abs(r1 - r2):
            if c1 > c2 and r1 > r2 or c2 > c1 and r2 > r1:
                min_c = min(c1, c2)
                min_r = min(r1, r2)
                return all(
                    self.state[COLUMNS[min_c + i] + str(min_r + i)] == ''
                    for i in range(1, abs(c1 - c2)))
            elif c1 > c2 and r2 > r1:
                return all(self.state[COLUMNS[c2 + i] + str(r2 - i)] == ''
                           for i in range(1, c1 - c2))
            else:
                return all(self.state[COLUMNS[c2 - i] + str(r2 + i)] == ''
                           for i in range(1, c2 - c1))

        return False

    def _update_state(self, frm, to, pt):
        self.state[frm] = ''
        self.state[to] = pt

    def _find_non_pawn(self, move, to, piece):
        if len(move) == 5:
            return move[1:3]

        p = piece[1]
        key = '' if len(move) == 3 else move[1]

        if p == 'r':
            return next(
                s for s, pt in self.state.items()
                if pt == piece and key in s and self._check_line(s, to))
        elif p == 'b':
            return next(
                s for s, pt in self.state.items()
                if pt == piece and key in s and self._check_diagonal(s, to))
        elif p == 'n':
            return next(s for s, pt in self.state.items() if pt == piece
                        and key in s and self._check_knight_move(s, to))
        else:
            return next(
                s for s, pt in self.state.items()
                if pt == piece and key in s and (
                    self._check_line(s, to) or self._check_diagonal(s, to)))

    def _find_pawn(self, move):
        pt = 'wp' if self.is_white_turn else 'bp'
        c = move[-2]
        r = int(move[-1])

        if len(move) == 2:
            if self.is_white_turn:
                origin = c + next(
                    str(i)
                    for i in range(r, 0, -1) if self.state[c + str(i)] == pt)
            else:
                origin = c + next(
                    str(i)
                    for i in range(r, 9) if self.state[c + str(i)] == pt)
        else:
            if self.state[move[-2:]] != '':
                origin = move[0] + (str(r - 1)
                                    if self.is_white_turn else str(r + 1))
            else:  # En passant
                nps = c + (str(r - 1) if self.is_white_turn else str(r + 1))
                self.state[nps] = ''
                origin = move[0] + nps[-1]

        return origin

    def _castle(self, move):
        row, color = ('1', 'w') if self.is_white_turn else ('8', 'b')
        if move.count('O') == 2:
            r = 'h' + row
            k_to = 'g' + row
            r_to = 'f' + row
        else:
            r = 'a' + row
            k_to = 'c' + row
            r_to = 'd' + row

        self._update_state('e' + row, k_to, color + 'k')
        self._update_state(r, r_to, color + 'r')

    def _promote(self, move):
        pt = ('w' if self.is_white_turn else 'b') + move[-1].lower()
        origin = move[0] + ('7' if self.is_white_turn else '2')
        self._update_state(origin, move[-4:-2], pt)

    def _parse_pgn_file(self, pgn):
        with open(pgn) as p:
            data = p.read()
            data = re.sub(r'{.*?}|\[.*?\]|[x]', '', data, flags=re.DOTALL)
            self.moves = re.findall(
                r'[a-h][a-h]?[1-8]=?[BKNRQ]?|O-O-?O?|[BKNRQ][a-h1-8]?[a-h1-8]?[a-h][1-8]',
                data)

    def next(self):
        if self.is_finished:
            return

        self._last_played_move_index += 1
        try:
            move = self.moves[self._last_played_move_index]
        except:
            self.is_finished = True
            return

        if 'O' in move:
            self._castle(move)

        elif '=' in move:
            self._promote(move)

        else:
            dest = move[-2:]
            if (move.islower()):
                pt = ('w' if self.is_white_turn else 'b') + 'p'
                origin = self._find_pawn(move)
            else:
                pt = ('w' if self.is_white_turn else 'b') + move[0].lower()
                origin = self._find_non_pawn(move, dest, pt)

            self._update_state(origin, dest, pt)

        self.is_white_turn = not self.is_white_turn
