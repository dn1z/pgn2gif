import os
import re
import glob
import argparse

import imageio
import numpy as np
from PIL import Image as img

columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
rows = ['1', '2', '3', '4', '5', '6', '7', '8']

black_square = img.new('RGBA', (60, 60), (75, 115, 153))
white_square = img.new('RGBA', (60, 60), (234, 233, 210))

bk = img.open('./images/bk.png')
bq = img.open('./images/bq.png')
bb = img.open('./images/bb.png')
bn = img.open('./images/bn.png')
br = img.open('./images/br.png')
bp = img.open('./images/bp.png')

wk = img.open('./images/wk.png')
wq = img.open('./images/wq.png')
wb = img.open('./images/wb.png')
wn = img.open('./images/wn.png')
wr = img.open('./images/wr.png')
wp = img.open('./images/wp.png')

def get_moves_from_pgn(file_path):
    with open(file_path) as pgn:
        data = pgn.read()        
        moves = re.findall(r'[a-h]x?[a-h]?[1-8]=?[BKNRQ]?|O-O-?O?|[BKNRQ][a-h1-8]?[a-h1-8]?x?[a-h][1-8]',data)
        return [move.replace('x','') for move in moves]


def point_of_square(move):
    c = columns.index(move[-2])
    r = 7 - rows.index(move[-1])
    if is_reversed:
        return ((7 - c) * 60, (7 - r) * 60)
    else:
        return (c * 60, r * 60)


def clear(point):
    if (point[0] + point[1]) % 120 == 0:
        board.paste(white_square, point, white_square)
    else:
        board.paste(black_square, point, black_square)


def update(move, turn):
    if not 'O' in move:
        if not '=' in move:
            to = point_of_square(move)
            frm = point_of_source(move, turn)

            clear(frm)
            if pieces[move[-2:]] != '':
                clear(to)

            if move[0] in ('N', 'K', 'Q', 'R', 'B'):
                exec('board.paste(w{0},to,w{0}) if turn == 0 else board.paste(b{0},to,b{0})'.format(move[0].lower()))
            else:
                board.paste(wp, to, wp) if turn == 0 else board.paste(bp, to, bp)
        else:
            # Pawn promotion e.g. c8=Q
            to = move[-4:-2]
            p = 'w' + move[-1].lower() if turn == 0 else 'b' + move[-1].lower()

            if turn == 0:
                frm = move[0] + str(int(move[-3]) - 1)
            else:
                frm = move[0] + str(int(move[-3]) + 1)

            update_pieces(frm, to, p)
            clear(point_of_square(frm))
            # Promotion with capture e.g. bc1=Q
            if len(move) == 5:
                clear(point_of_square(to))
            exec(f'board.paste({p},{point_of_square(to)},{p})')
    else:
        row = '1' if turn == 0 else '8'
        t = 'w' if turn == 0 else 'b'
        k = 'e' + row
        if move.count('O') == 2:
            r = 'h' + row
            k_to = 'g' + row
            r_to = 'f' + row
        else:
            r = 'a' + row
            k_to = 'c' + row
            r_to = 'd' + row 

        update_pieces(k, k_to, t + 'k')
        update_pieces(r, r_to, t + 'r')
        clear(point_of_square(r)) 
        clear(point_of_square(k))
        exec('board.paste({0},point_of_square({1}),{0})'.format(t + 'k', 'k_to'))
        exec('board.paste({0},point_of_square({1}),{0})'.format(t + 'r', 'r_to'))



def check_knight_move(sqr1, sqr2):
    v = abs(columns.index(sqr1[0]) - columns.index(sqr2[0]))
    if v == 1:
        return abs(rows.index(sqr1[1]) - rows.index(sqr2[1])) == 2
    elif v == 2:
        return abs(rows.index(sqr1[1]) - rows.index(sqr2[1])) == 1
    return False


def check_line(sqr1, sqr2):
    c1 = sqr1[0]
    c2 = sqr2[0]
    r1 = int(sqr1[1])
    r2 = int(sqr2[1])
    if r1 == r2:
        i1 = columns.index(c1)
        i2 = columns.index(c2)
        return all(pieces[columns[i] + str(r1)] == '' for i in range(min(i1, i2) + 1, max(i1, i2)))
    elif c1 == c2:
        return all(pieces[c1 + str(i)] == '' for i in range(min(r1, r2) + 1, max(r1, r2)))
    return False


def check_diagonal(sqr1, sqr2):
    c1 = columns.index(sqr1[0])
    c2 = columns.index(sqr2[0])
    r1 = int(sqr1[1])
    r2 = int(sqr2[1])
    if abs(c1 - c2) == abs(r1 - r2):
        if c1 > c2 and r1 > r2 or c2 > c1 and r2 > r1:
            min_c = min(c1, c2)
            min_r = min(r1, r2)
            return all(pieces[columns[min_c+i] + str(min_r + i)] == '' for i in range(1, abs(c1-c2)))

        elif c1 > c2 and r2 > r1:
            return all(pieces[columns[c2 + i] + str(r2 - i)] == '' for i in range(1, c1 - c2))

        else:
            return all(pieces[columns[c2 - i] + str(r2 + i)] == '' for i in range(1, c2 - c1))
    return False


def update_pieces(frm, to, piece_type):
    pieces[frm] = ''
    pieces[to] = piece_type


def point_of_source(move, turn):
    # Presents which square move has played
    to = move[-2:]
    # Presents which square move came from
    source = ''
    # Presents piece type
    p = ''

    c = move[-2]
    r = int(move[-1])

    if len(move) == 5:
        source = move[1:3]
        p = move[0].lower()

    elif move.islower():
        p = 'wp' if turn == 0 else 'bp'
        # Pushing pawn e.g. e4
        if len(move) == 2:
            if turn == 0:
                source = c + next(str(i) for i in range(r, 0, -1) if pieces[c + str(i)] == p)
            else:
                source = c + next(str(i) for i in range(r, 9) if pieces[c + str(i)] == p)
        # Capturing pawn e.g. ed5
        elif len(move) == 3:
            if pieces[move[-2:]] != '':
                if turn == 0:
                    source = move[0] + str(r - 1)
                else:
                    source = move[0] + str(r + 1)
            # En Passant
            else:
                if turn == 0:
                    next_pawn = c + str(r - 1)
                else:
                    next_pawn = c + str(r + 1)
                clear(point_of_square(next_pawn))
                pieces[next_pawn] = ''
                source = move[0] + next_pawn[-1]

    elif move[0] == 'K':
        p = 'wk' if turn == 0 else 'bk'
        source = next(sq for sq, pt in pieces.items() if pt == p)

    elif move[0] == 'B':
        p = 'wb' if turn == 0 else 'bb'
        if len(move) == 3:
            source = next(sq for sq, pt in pieces.items() if pt == p and check_diagonal(sq, to))
        else:
            indicator = move[1]
            source = next(sq for sq, pt in pieces.items() if pt == p and indicator in sq and check_diagonal(sq, to))

    elif move[0] == 'R':
        p = 'wr' if turn == 0 else 'br'
        # e.g. Ra3
        if len(move) == 3:
            try:
                source = c + next(row for row in rows if pieces[c + str(row)] == p and check_line(c + str(row), to))

            except:
                source = next(col for col in columns if pieces[col + str(r)] == p and check_line(col + str(r), to)) + str(r)
        # e.g. Raa3
        else:
            indicator = move[1]
            if indicator in columns:
                source = indicator + next(row for row in rows if pieces[indicator + row] == p)
            else:
                source = next(col for col in columns if pieces[col + indicator] == p) + indicator

    elif move[0] == 'Q':
        p = 'wq' if turn == 0 else 'bq'
        if len(move) == 3:
            source = next(sq for sq, pt in pieces.items() if pt == p and (check_line(sq, to) or check_diagonal(sq, to)))
        else:
            indicator = move[1]
            source = next(sq for sq, pt in pieces.items() if pt == p and indicator in (move[0], move[1]))

    elif move[0] == 'N':
        p = 'wn' if turn == 0 else 'bn'
        if len(move) == 3:
            source = next(sq for sq, pt in pieces.items() if pt == p and check_knight_move(sq, to))
        else:
            indicator = move[1]
            source = next(sq for sq, pt in pieces.items() if pt == p and indicator in sq and check_knight_move(sq, to))

    update_pieces(source, to, p)
    return point_of_square(source)


def create_gif(file_name, out_name, duration, output_dir, reverse):
    global is_reversed
    is_reversed = reverse 

    global board
    if is_reversed:
        board = img.open('./images/board2.png')
    else:
        board = img.open('./images/board.png')
    
    global pieces
    pieces = {'a8': 'br', 'b8': 'bn', 'c8': 'bb', 'd8': 'bq', 'e8': 'bk', 'f8': 'bb', 'g8': 'bn', 'h8': 'br',
              'a7': 'bp', 'b7': 'bp', 'c7': 'bp', 'd7': 'bp', 'e7': 'bp', 'f7': 'bp', 'g7': 'bp', 'h7': 'bp',
              'a6': '', 'b6': '', 'c6': '', 'd6': '', 'e6': '', 'f6': '', 'g6': '', 'h6': '',
              'a5': '', 'b5': '', 'c5': '', 'd5': '', 'e5': '', 'f5': '', 'g5': '', 'h5': '',
              'a4': '', 'b4': '', 'c4': '', 'd4': '', 'e4': '', 'f4': '', 'g4': '', 'h4': '',
              'a3': '', 'b3': '', 'c3': '', 'd3': '', 'e3': '', 'f3': '', 'g3': '', 'h3': '',
              'a2': 'wp', 'b2': 'wp', 'c2': 'wp', 'd2': 'wp', 'e2': 'wp', 'f2': 'wp', 'g2': 'wp', 'h2': 'wp',
              'a1': 'wr', 'b1': 'wn', 'c1': 'wb', 'd1': 'wq', 'e1': 'wk', 'f1': 'wb', 'g1': 'wn', 'h1': 'wr'}

    images = [np.array(board)]
    moves = get_moves_from_pgn(file_name)

    for i,move in enumerate(moves):
        update(move, i % 2)
        images.append(np.array(board))

    for i in range(3):
        images.append(np.array(board))

    imageio.mimsave(f'{output_dir}/{out_name}', images, duration=duration)


def process_file(pgn, duration, output_dir, reverse):
    """
    Act as a calling function for the createGif.
    Handles one pgn file at a time.

    :pgn: Name of the pgn file
    :duration: Speed of the pieces moving in a gif
    """
    basename = os.path.basename(pgn)
    name = basename[:-4] + '.gif'
    if name in os.listdir('.'):
        print("gif with name %s already exists." % name)
    else:
        print('Creating ' + name, end='.... ')
        create_gif(pgn, name, duration, output_dir, reverse)
        print('done')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', help='path to the pgn file/folder', default=os.getcwd() + '/')
    parser.add_argument('-s', '--speed', help='Speed with which pieces move in gif.', default=0.4)
    parser.add_argument('-o', '--out', help='Name of the output folder', default=os.getcwd())
    parser.add_argument('-r', '--reverse', help='Whether reverse board or not', default=False)
    args = parser.parse_args()

    print('pgn2gif')
    if os.path.isfile(args.path):
        process_file(args.path, args.speed, args.out, args.reverse)

    elif os.path.isdir(args.path):
        for pgn in glob.glob(args.path + '*.pgn'):
            process_file(pgn, args.speed, args.out, args.reverse)
