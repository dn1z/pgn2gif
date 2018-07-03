import glob
import os
import re

from PIL import Image as img

path = os.path.dirname(__file__)

columns = ['a' , 'b' , 'c' , 'd' , 'e' , 'f' , 'g' , 'h']
rows = ['1' , '2' , '3' , '4' , '5' , '6' , '7' , '8']

black = img.new('RGBA' ,(80,80) ,(75,115,153))
white = img.new('RGBA' ,(80,80) ,(234,233,210))
board = img.open(path + "/temp/board.png")

bk = img.open(path + '/pieces/bk.png')
bq = img.open(path + '/pieces/bq.png')
bb = img.open(path + '/pieces/bb.png')
bn = img.open(path + '/pieces/bn.png')
br = img.open(path + '/pieces/br.png')
bp = img.open(path + '/pieces/bp.png')

wk = img.open(path + '/pieces/wk.png')
wq = img.open(path + '/pieces/wq.png')
wb = img.open(path + '/pieces/wb.png')
wn = img.open(path + '/pieces/wn.png')
wr = img.open(path + '/pieces/wr.png')
wp = img.open(path + '/pieces/wp.png')

pieces = {'a8' : 'br','b8' : 'bn','c8' : 'bb','d8' : 'bq','e8' : 'bk','f8' : 'bb','g8' : 'bn','h8' : 'br',
          'a7' : 'bp','b7' : 'bp','c7' : 'bp','d7' : 'bp','e7' : 'bp','f7' : 'bp','g7' : 'bp','h7' : 'bp',
          'a6' : '','b6' : '','c6' : '','d6' : '','e6' : '','f6' : '','g6' : '','h6' : '',
          'a5' : '','b5' : '','c5' : '','d5' : '','e5' : '','f5' : '','g5' : '','h5' : '',
          'a4' : '','b4' : '','c4' : '','d4' : '','e4' : '','f4' : '','g4' : '','h4' : '',
          'a3' : '','b3' : '','c3' : '','d3' : '','e3' : '','f3' : '','g3' : '','h3' : '',
          'a2' : 'wp','b2' : 'wp','c2' : 'wp','d2' : 'wp','e2' : 'wp','f2' : 'wp','g2' : 'wp','h2' : 'wp',
          'a1' : 'wr','b1' : 'wn','c1' : 'wb','d1' : 'wq','e1' : 'wk','f1' : 'wb','g1' : 'wn','h1' : 'wr'}



def create():
    for pgn in glob.glob(path + "/pgn/*.pgn"):
        if os.path.isfile(path +  "/gifs/" +  os.path.splitext(pgn)[0] + ".gif"):
           continue
        else:
            moves = get_moves(pgn)
            for i in range(10):
                update(moves[i] , i % 2)
                #board.save('{0}/temp/b{1}.png'.format(path,i+1))
            print(pieces)
            board.show()
                           
            
def get_moves(file_path : str) -> list:
    pgn = open(file_path)
    move_lines = [line for line in pgn.readlines() if not line[0] == "[" and not line[0] == "\n"]
    pgn.close()

    moves = []
    for move_line in move_lines:
        for move in re.split(r'\d\.', move_line)[1::]:
            moves.extend(move.split(' ')[1:3])

    for i , item in enumerate(moves):
        moves[i] = item.rstrip().strip('+').replace('x','')
    return moves

def pixels_from_square(move : str) -> tuple:  
    m = move[-2:]
    i1 = columns.index(m[0])
    i2 = 7 - rows.index(m[1])
    return (i1 * 80 , i2 * 80)

def are_diagonal(crd1 : str, crd2 : str) -> bool:
    p1 = pixels_from_square(crd1)
    p2 = pixels_from_square(crd2)
    return abs(p1[0] - p2[0]) == abs(p1[1] - p2[1])     

def are_linear(crd1 : str,crd2 : str) -> bool:
    return crd1[0] == crd2[0] or crd2[0] == crd1

def clear(crd : tuple):
    if (crd[0] + crd[1]) % 160 == 0:
        board.paste(white,crd,white)
    else:
        board.paste(black,crd,black)

def castle(move : str , turn : str):
    if turn == 0:
        k = 'wk'
        r = 'wr'
        row = '1'
    else:
        k = 'bk'
        r = 'br'
        row = '8'
    if move.count('O') == 2:
        k_sq = 'g' + row
        r_sq = 'f' + row
        pieces['e' + row] = ''
        pieces['h' + row] = ''
        pieces['g' + row] = k
        pieces['f' + row] = r
        clear(pixels_from_square('e' + row))
        clear(pixels_from_square('h' + row))
        exec(f'board.paste({k},{pixels_from_square(k_sq)},{k})')
        exec(f'board.paste({r},{pixels_from_square(r_sq)},{r})')

def update(move : str , turn : int):
    if not 'O' in move:
        if not '=' in move:
            destination = pixels_from_square(move)
            home = coming_square(move , turn)

            clear(home)
            clear(destination)  

            if move[0] in ('N' , 'K' , 'Q' , 'R' , 'B'):
                exec('board.paste(w{0},destination,w{0}) if turn == 0 else board.paste(b{0},destination,b{0})'.format(move[0].lower()))
            else:
                board.paste(wp,destination,wp) if turn == 0 else board.paste(bp,destination,bp)  
        else:
            # Pawn promotion e.g. c8=Q
            to = move[-4:-2]
            p = 'w' + move[-1].lower() if turn == 0 else 'b' + move[-1].lower()

            if turn == 0:
                comes_from = move[0] + str(int(move[-3]) -1)
            else:
                comes_from = move[0] + str(int(move[-3]) +1)
            update_dict(comes_from,to,p)
            clear(pixels_from_square(comes_from))
            # Promotion with captures
            if len(move) == 5:
                clear(pixels_from_square(to))
            exec(f'board.paste({p},{pixels_from_square(to)},{p})')
    else:
        castle(move , turn)

def are_L_shape(crd1 : str , crd2 : str) -> bool:
    v = abs(columns.index(crd1[0]) - columns.index(crd2[0]))
    if  v == 1:
        return abs(rows.index(crd1[1]) - rows.index(crd2[1])) == 2
    elif v == 2:
        return abs(rows.index(crd1[1]) - rows.index(crd2[1])) == 1
    return False

def update_dict(frm : str, to : str, piece_type : str):
    pieces[frm] = ''
    pieces[to] = piece_type 

def coming_square(move : str , turn : int) -> tuple:
    # Presents which square move has played
    to = move[-2:]
    # Presents which square move came from
    comes_from = ''
    # Presents piece type
    p = ''

    c = move[-2]
    r = int(move[-1])


    if len(move) == 5:
        comes_from = move[1:3]
        p = move[0].lower()

    elif move.islower():
        p = 'wp' if turn == 0 else 'bp'
        # Pushing pawn e.g. e4
        if len(move) == 2:
            if turn == 0:
                comes_from = c + next(str(i) for i in range(r,0,-1) if pieces[c+str(i)] == p)
            else:
                comes_from = c + next(str(i) for i in range(r,9) if pieces[c+str(i)] == p) 
        # Capturing pawn e.g. ed5
        elif len(move) == 3:
            if pieces[move[-2:]] != '': 
                if turn == 0:
                    comes_from = move[0] + str(r-1)
                else:
                    comes_from = move[0] + str(r+1)
            # En Passant 
            else:
                if turn == 0:
                    next_pawn = c + str(r - 1)
                else:
                    next_pawn = c + str(r + 1)
                clear(pixels_from_square(next_pawn))
                pieces[next_pawn] = ''
                comes_from = move[0] + next_pawn[-1]
   
    elif move[0] == 'K':
        p = 'wk' if turn == 0 else 'bk'
        comes_from = next(sq for sq,pt in pieces.items() if pt == p)

    elif move[0] == 'B':
        p = 'wb' if turn == 0 else 'bb'
        if len(move) == 3:
            comes_from = next(sq for sq,pt in pieces.items() if pt == p and are_diagonal(sq,to))
        else:
            indicator = move[1]
            comes_from = next(sq for sq,pt in pieces.items() if pt==p and indicator in move and are_diagonal(sq,to))

    elif move[0] == 'R':
        p = 'wr' if turn == 0 else 'br'
        # e.g. Ra3
        if len(move) == 3:
            try:
                comes_from = c + next(row for row in rows if pieces[c + str(row)] == p)
            except:
                comes_from = next(col for col in columns if pieces[col + str(r)] == p) + str(r) 
        # e.g. Raa3
        else:
            indicator = move[1]
            if indicator in columns:
                comes_from = indicator + next(row for row in rows if pieces[indicator+row]==p)
            else:
                comes_from = next(col for col in columns if pieces[col+indicator]==p) + indicator

    elif move[0] == 'Q':
        p = 'wq' if turn == 0 else 'bq'
        if len(move) == 3:
            comes_from = next(sq for sq,pt in pieces.items() if pt == p and (are_diagonal(sq,to) or are_linear(sq,to)))
        else:
            indicator = move[1]
            comes_from = next(sq for sq,pt in pieces.items() if pt == p and indicator in (move[0],move[1]))

    elif move[0] == 'N':
        p = 'wn' if turn == 0 else 'bn'
        if len(move) == 3:
            comes_from = next(sq for sq,pt in pieces.items() if pt == p and are_L_shape(sq,to))
        else:
            indicator = move[1]
            comes_from = next(sq for sq,pt in pieces.items() if pt == p and indicator in sq)

    update_dict(comes_from,to,p)
    return pixels_from_square(comes_from)

if __name__ == '__main__':
    create()
