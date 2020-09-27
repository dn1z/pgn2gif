try:
    from . import chess
except ImportError:
    import chess

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
    ws_color : str, optional
        Color of white squares in hex or string
    bs_color : str, optional
        Color of black squares in hex or string
    '''

    _BOARD_SIZE = 480
    _SQ_SIZE = _BOARD_SIZE // 8

    def __init__(self, reverse=False, duration=0.4, ws_color='#f0d9b5', bs_color='#b58863'):
        self.duration = duration

        self._pieces = {}
        self._reverse = reverse
        self._ws_color = ws_color
        self._bs_color = bs_color
        self._should_redraw = True

    @property
    def reverse(self):
        return self._reverse

    @reverse.setter
    def reverse(self, reverse):
        self._reverse = reverse
        self._should_redraw = True

    @property
    def ws_color(self):
        return self._ws_color

    @ws_color.setter
    def ws_color(self, ws_color):
        self._ws_color = ws_color
        self._should_redraw = True

    @property
    def bs_color(self):
        return self._bs_color

    @bs_color.setter
    def bs_color(self, bs_color):
        self._bs_color = bs_color
        self._should_redraw = True

    def _draw_board(self):
        if not self._pieces:
            for asset in (Path(__file__).parent/'assets').iterdir():
                self._pieces[asset.stem] = Image.open(asset)

        self._ws = Image.new('RGBA', (self._SQ_SIZE, self._SQ_SIZE),
                             self.ws_color)
        self._bs = Image.new('RGBA', (self._SQ_SIZE, self._SQ_SIZE),
                             self.bs_color)

        self._initial_board = Image.new(
            'RGBA', (self._BOARD_SIZE, self._BOARD_SIZE))
        self._update_board_image(self._initial_board, chess.INITIAL_STATE,
                                 list(chess.INITIAL_STATE.keys()))

        self._should_redraw = False

    def _coordinates_of_square(self, square):
        c = ord(square[0]) - 97
        r = int(square[1]) - 1

        if self.reverse:
            return ((7 - c) * self._SQ_SIZE, r * self._SQ_SIZE)
        else:
            return (c * self._SQ_SIZE, (7 - r) * self._SQ_SIZE)

    def _update_board_image(self, board_image, game_state, changed_squares):
        for square in changed_squares:
            crd = self._coordinates_of_square(square)

            if sum(crd) % (self._SQ_SIZE * 2) == 0:
                board_image.paste(self._ws, crd, self._ws)
            else:
                board_image.paste(self._bs, crd, self._bs)

            piece = game_state[square]
            if piece:
                img = self._pieces[piece]
                board_image.paste(img, crd, img)

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
        if self._should_redraw:
            self._draw_board()

        board_image = self._initial_board.copy()
        frames = [board_image.copy()]

        game = chess.ChessGame(pgn)

        while not game.is_finished:
            previous = game.state.copy()
            game.next()
            self._update_board_image(board_image, game.state, [
                s for s in game.state.keys() if game.state[s] != previous[s]])
            frames.append(board_image.copy())

        last = frames[len(frames) - 1]
        for _ in range(3):
            frames.append(last)

        if not out_path:
            out_path = Path(pgn).stem + '.gif'

        frames[0].save(out_path, format="GIF", append_images=frames[1:],
                       optimize=True, save_all=True, duration=int(self.duration * 1000), loop=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path', nargs='+', help='Path to the pgn file(s)')
    parser.add_argument(
        '-d', '--duration', help='Duration between moves in seconds', default=0.4)
    parser.add_argument(
        '-o', '--out', help='Name of the output folder', default=Path.cwd())
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

    creator = PgnToGifCreator(
        args.reverse, float(args.duration), args.white_square_color, args.black_square_color)
    for pgn in args.path:
        f = Path(pgn).stem + '.gif'
        creator.create_gif(pgn, Path(args.out) / f)


if __name__ == '__main__':
    main()
