from __future__ import print_function

import os
import glob
import argparse

import imageio
from PIL import Image
from numpy import array

from . import chess

cwd = os.getcwd()
os.chdir(os.path.dirname(__file__))

# Lazily load images
bk = Image.open('./assets/bk.png')
bq = Image.open('./assets/bq.png')
bb = Image.open('./assets/bb.png')
bn = Image.open('./assets/bn.png')
br = Image.open('./assets/br.png')
bp = Image.open('./assets/bp.png')

wk = Image.open('./assets/wk.png')
wq = Image.open('./assets/wq.png')
wb = Image.open('./assets/wb.png')
wn = Image.open('./assets/wn.png')
wr = Image.open('./assets/wr.png')
wp = Image.open('./assets/wp.png')

os.chdir(cwd)

# You can change the size of gif (BOARD_EDGE x BOARD_EDGE)
# But it is not recommended unless you update piece images to fit square
BOARD_EDGE = 480
SQUARE_EDGE = BOARD_EDGE // 8


def coordinates_of_square(square):
    c = ord(square[0]) - 97
    r = int(square[1]) - 1
    if reverse:
        return ((7 - c) * SQUARE_EDGE, r * SQUARE_EDGE)
    else:
        return (c * SQUARE_EDGE, (7 - r) * SQUARE_EDGE)


def clear(image, crd):
    if (crd[0] + crd[1]) % (SQUARE_EDGE * 2) == 0:
        image.paste(white_square, crd, white_square)
    else:
        image.paste(black_square, crd, black_square)


def apply_move(board_image, current, previous):
    changed = [s for s in current.keys() if current[s] != previous[s]]

    for square in changed:
        crd = coordinates_of_square(square)
        clear(board_image, crd)

        if current[square] != '':
            exec('board_image.paste({0}, crd, {0})'.format(current[square]))


def create_gif(pgn, output_dir, out_name, duration):
    board_image = initial_board.copy()
    images = [array(board_image)]

    game = chess.ChessGame()
    moves = chess.get_moves_from_pgn(pgn)

    for move in moves:
        previous = game.state.copy()
        game.push(move)
        apply_move(board_image, game.state, previous)
        images.append(array(board_image))

    last = images[len(moves)]
    for i in range(3):
        images.append(last)

    imageio.mimsave(output_dir + '/' + out_name, images, duration=duration)


def process_file(pgn, duration, output_dir):
    name = os.path.basename(pgn)[:-4] + '.gif'
    if name in os.listdir(output_dir):
        print('gif with name %s already exists.' % name)
    else:
        print('Creating ' + name, end='... ')
        create_gif(pgn, output_dir, name, duration)
        print('done')


def generate_board():
    global initial_board
    initial_board = Image.new('RGB', (BOARD_EDGE, BOARD_EDGE))

    for i in range(0, BOARD_EDGE, SQUARE_EDGE):
        for j in range(0, BOARD_EDGE, SQUARE_EDGE):
            clear(initial_board, (i, j))

    row = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    order = ('w', 'b') if reverse else ('b', 'w')

    for i in range(8):
        col = SQUARE_EDGE * i
        exec('initial_board.paste({0}, (col, 0), {0})'
            .format(order[0] + row[i]))
        exec('initial_board.paste({0}, (col, BOARD_EDGE - SQUARE_EDGE), {0})'
            .format(order[1] + row[i]))

        exec('initial_board.paste({0}p, (col, SQUARE_EDGE), {0}p)'
            .format(order[0]))
        exec(
            'initial_board.paste({0}p, (col, BOARD_EDGE - (SQUARE_EDGE * 2)), {0}p)'
            .format(order[1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--path',
        help='Path to the pgn file/folder',
        default=os.getcwd() + '/')
    parser.add_argument(
        '-d', '--delay', help='Delay between moves in seconds', default=0.4)
    parser.add_argument(
        '-o', '--out', help='Name of the output folder', default=os.getcwd())
    parser.add_argument(
        '-r', '--reverse', help='Reverse board', action='store_true')
    parser.add_argument(
        '--black-square-color',
        help='Color of black squares in hex',
        default='#4B7399')
    parser.add_argument(
        '--white-square-color',
        help='Color of white squares in hex',
        default='#EAE9D2')
    args = parser.parse_args()

    global reverse
    reverse = args.reverse

    global white_square, black_square
    white_square = Image.new('RGBA', (SQUARE_EDGE, SQUARE_EDGE),
                             args.white_square_color)
    black_square = Image.new('RGBA', (SQUARE_EDGE, SQUARE_EDGE),
                             args.black_square_color)

    generate_board()

    if os.path.isfile(args.path):
        process_file(args.path, args.delay, args.out)

    elif os.path.isdir(args.path):
        for pgn in glob.glob(args.path + '*.pgn'):
            process_file(pgn, args.delay, args.out)


if __name__ == '__main__':
    main()
