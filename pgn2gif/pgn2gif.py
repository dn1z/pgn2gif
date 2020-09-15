try:
    from . import chess
except ImportError:
    import chess

import os
import argparse

import imageio
from PIL import Image
from numpy import array


# You can change the size of gif (BOARD_EDGE x BOARD_EDGE)
# But it is not recommended unless piece images are updated to fit into squares
BOARD_EDGE = 480
SQUARE_EDGE = BOARD_EDGE // 8


def coordinates_of_square(square):
    c = ord(square[0]) - 97
    r = int(square[1]) - 1
    if reverse:
        return ((7 - c) * SQUARE_EDGE, r * SQUARE_EDGE)
    else:
        return (c * SQUARE_EDGE, (7 - r) * SQUARE_EDGE)


def reset_square_color(image, square):
    crd = coordinates_of_square(square)

    if (crd[0] + crd[1]) % (SQUARE_EDGE * 2) == 0:
        image.paste(white_square, crd, white_square)
    else:
        image.paste(black_square, crd, black_square)


def update_board_image(board_image, game_state, changed_squares):
    for square in changed_squares:
        reset_square_color(board_image, square)
        piece = game_state[square]

        if piece:
            paste_image_into_square(
                board_image, piece, coordinates_of_square(square))


def paste_image_into_square(image, piece, crd):
    exec('image.paste({0}, {1}, {0})'.format(piece, crd))


def load_assets():
    cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

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
    globals().update(locals())

    os.chdir(cwd)


def generate_board():
    global initial_board
    initial_board = Image.new('RGB', (BOARD_EDGE, BOARD_EDGE))
    update_board_image(initial_board, chess.INITIAL_STATE,
                       list(chess.INITIAL_STATE.keys()))


def create_gif(pgn, gif_path, duration):
    board_image = initial_board.copy()
    images = [array(board_image)]

    game = chess.ChessGame(pgn=pgn)

    while not game.is_finished:
        previous = game.state.copy()
        game.next()
        update_board_image(board_image, game.state, [
                           s for s in game.state.keys() if game.state[s] != previous[s]])
        images.append(array(board_image))

    last = images[len(images) - 1]
    for _ in range(3):
        images.append(last)

    imageio.mimsave(gif_path, images, duration=duration)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path', nargs='*', help='Path to the pgn file')
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

    if not args.path:
        print('Please specify path of pgn file(s)')
        return

    global reverse
    reverse = args.reverse

    global white_square, black_square
    white_square = Image.new('RGBA', (SQUARE_EDGE, SQUARE_EDGE),
                             args.white_square_color)
    black_square = Image.new('RGBA', (SQUARE_EDGE, SQUARE_EDGE),
                             args.black_square_color)

    load_assets()
    generate_board()

    for pgn in args.path:
        try:
            name = os.path.basename(pgn)[:-4] + '.gif'
            if name in os.listdir(args.out):
                print('A gif with name {0} already exists.'.format(name))
            else:
                out_path = os.path.join(args.out, name)
                create_gif(pgn, out_path, args.delay)
                print('Created {0}'.format(name))
        except Exception as e:
            print(e)
            print("Error processing pgn file {0}".format(pgn))


if __name__ == '__main__':
    main()
