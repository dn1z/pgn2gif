try:
    from . import chess
except ImportError:
    import chess

import os
import argparse
from pathlib import Path

from PIL import Image


class PgnToGifCreator:
    '''
    PGN to GIF creator class
    Parameters
    ----------
    reverse : bool, optional
        Whether to reverse board or not
    duration : float, optional
        Duration between moves in seconds
    white_square_color : str, optional
        Color of white squares in hex or string
    black_square_color : str, optional
        Color of black squares in hex or string
    '''

    __BOARD_SIZE = 480
    __SQ_SIZE = __BOARD_SIZE // 8

    def __init__(self, reverse=False, duration=0.4, white_square_color='#f0d9b5', black_square_color='#b58863'):
        self.__pieces = {}
        self.__reverse = reverse
        self.__duration = duration

        self.__load_pieces()
        self.__generate_board(white_square_color, black_square_color)

    def __generate_board(self, white_square_color, black_square_color):
        self.__white_square = Image.new('RGBA', (self.__SQ_SIZE, self.__SQ_SIZE),
                                        white_square_color)
        self.__black_square = Image.new('RGBA', (self.__SQ_SIZE, self.__SQ_SIZE),
                                        black_square_color)

        self.__initial_board = Image.new(
            'RGBA', (self.__BOARD_SIZE, self.__BOARD_SIZE))
        self.__update_board_image(self.__initial_board, chess.INITIAL_STATE,
                                  list(chess.INITIAL_STATE.keys()))

    def __load_pieces(self):
        cwd = os.getcwd()
        assets_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'assets')
        os.chdir(assets_dir)

        for asset in os.listdir(assets_dir):
            self.__pieces[os.path.splitext(asset)[0]] = Image.open(asset)

        os.chdir(cwd)

    def __paste_image_into_board(self, board_image, pasted_image, coordinates):
        board_image.paste(pasted_image, coordinates, pasted_image)

    def __update_board_image(self, board_image, game_state, changed_squares):
        for square in changed_squares:
            crd = self.__coordinates_of_square(square)

            if sum(crd) % (self.__SQ_SIZE * 2) == 0:
                self.__paste_image_into_board(
                    board_image, self.__white_square, crd)
            else:
                self.__paste_image_into_board(
                    board_image, self.__black_square, crd)

            piece = game_state[square]
            if piece:
                self.__paste_image_into_board(
                    board_image, self.__pieces[piece], crd)

    def __coordinates_of_square(self, square):
        c = ord(square[0]) - 97
        r = int(square[1]) - 1

        if self.__reverse:
            return ((7 - c) * self.__SQ_SIZE, r * self.__SQ_SIZE)
        else:
            return (c * self.__SQ_SIZE, (7 - r) * self.__SQ_SIZE)

    def create_gif(self, pgn, out_path=None):
        '''
        Creates gif of pgn with same name.
        player1-player2.pgn -> player1-player2.gif (or as out_path)
        PARAMETERS
        -----------
        pgn : str
            Path of pgn file
        out_path : str, optional
            Output path of gif
        '''
        board_image = self.__initial_board.copy()
        frames = [board_image.copy()]

        game = chess.ChessGame(pgn)

        while not game.is_finished:
            previous = game.state.copy()
            game.next()
            self.__update_board_image(board_image, game.state, [
                s for s in game.state.keys() if game.state[s] != previous[s]])
            frames.append(board_image.copy())

        last = frames[len(frames) - 1]
        for _ in range(3):
            frames.append(last)

        if not out_path:
            out_path = os.path.join(os.getcwd(), Path(pgn).stem + '.gif')

        frames[0].save(out_path, format="GIF", append_images=frames[1:],
                       optimize=True, save_all=True, duration=int(self.__duration * 1000), loop=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path', nargs='*', help='Path to the pgn file(s)')
    parser.add_argument(
        '-d', '--duration', help='Duration between moves in seconds', default=0.4)
    parser.add_argument(
        '-o', '--out', help='Name of the output folder', default=os.getcwd())
    parser.add_argument(
        '-r', '--reverse', help='Reverse board', action='store_true')
    parser.add_argument(
        '--black-square-color',
        help='Color of black squares in hex or string',
        default='#b58863')
    parser.add_argument(
        '--white-square-color',
        help='Color of white squares in hex or string',
        default='#f0d9b5')
    args = parser.parse_args()

    if not args.path:
        return

    creator = PgnToGifCreator(
        args.reverse, float(args.duration), args.white_square_color, args.black_square_color)
    for pgn in args.path:
        f = Path(pgn).stem + '.gif'
        out_path = os.path.join(args.out, f)
        creator.create_gif(pgn, out_path)


if __name__ == '__main__':
    main()
