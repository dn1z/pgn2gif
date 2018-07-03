import os
import re

import imageio
import numpy as np
from PIL import Image as img

path = os.path.dirname(__file__)

columns = ['a' , 'b' , 'c' , 'd' , 'e' , 'f' , 'g' , 'h']
rows = ['1' , '2' , '3' , '4' , '5' , '6' , '7' , '8']

black_square = img.new('RGBA' ,(80,80) ,(75,115,153))
white_square = img.new('RGBA' ,(80,80) ,(234,233,210))
board = img.open(path + "/images/board.png")

bk = img.open(path + '/images/bk.png')
bq = img.open(path + '/images/bq.png')
bb = img.open(path + '/images/bb.png')
bn = img.open(path + '/images/bn.png')
br = img.open(path + '/images/br.png')
bp = img.open(path + '/images/bp.png')

wk = img.open(path + '/images/wk.png')
wq = img.open(path + '/images/wq.png')
wb = img.open(path + '/images/wb.png')
wn = img.open(path + '/images/wn.png')
wr = img.open(path + '/images/wr.png')
wp = img.open(path + '/images/wp.png') 
            
def get_moves(file_path : str) -> list:
    pgn = open(file_path)
    move_lines = [line for line in pgn.readlines() if not line[0] == "[" and not line[0] == "\n"]
    pgn.close()
    
    moves = []
    for move_line in move_lines:
        for move in re.split(r'\d+\.', move_line):
            moves.extend(move.split(' '))

    results = ('0-1\n','1-0\n','1/2-1/2\n')
    return [move.rstrip().strip('+').strip('#').replace('x','') for move in moves if len(move)>=2 and move not in results]

def pixels_from_square(move : str) -> tuple:  
    m = move[-2:]
    i1 = columns.index(m[0])
    i2 = 7 - rows.index(m[1])
    return (i1 * 80 , i2 * 80)

def clear(crd : tuple):
    if (crd[0] + crd[1]) % 160 == 0:
        board.paste(white_square,crd,white_square)
    else:
        board.paste(black_square,crd,black_square)

def update(move : str , turn : int):
    if not 'O' in move:
        if not '=' in move:
            to = pixels_from_square(move)
            frm = source_of_move(move , turn)

            clear(frm)
            clear(to)  

            if move[0] in ('N' , 'K' , 'Q' , 'R' , 'B'):
                exec('board.paste(w{0},to,w{0}) if turn == 0 else board.paste(b{0},to,b{0})'.format(move[0].lower()))
            else:
                board.paste(wp,to,wp) if turn == 0 else board.paste(bp,to,bp)  
        else:
            # Pawn promotion e.g. c8=Q
            to = move[-4:-2]
            p = 'w' + move[-1].lower() if turn == 0 else 'b' + move[-1].lower()

            if turn == 0:
                frm = move[0] + str(int(move[-3]) -1)
            else:
                frm = move[0] + str(int(move[-3]) +1)
            
            update_pieces(frm,to,p)
            clear(pixels_from_square(frm))
            # Promotion with capture e.g. bc3=Q
            if len(move) == 5:
                clear(pixels_from_square(to))
            exec(f'board.paste({p},{pixels_from_square(to)},{p})')
    else:
        if turn == 0:
            k = 'wk' ; r = 'wr' ; row = '1'
        else:
            k = 'bk' ; r = 'br' ; row = '8'
        kl = 'e' + row
        if move.count('O') == 2:
            ks = 'g'+row
            rs = 'f'+row
            clear(pixels_from_square('h'+row))
            update_pieces('h'+row,rs,r)
        else:
            ks = 'c' + row
            rs = 'd' + row
            clear(pixels_from_square('a'+row))
            update_pieces('a'+row,rs,r)

        update_pieces(kl,ks,k)
        clear(pixels_from_square(kl))
        exec(f'board.paste({k},{pixels_from_square(ks)},{k})')
        exec(f'board.paste({r},{pixels_from_square(rs)},{r})')

def check_knight_move(crd1 : str , crd2 : str) -> bool:
    v = abs(columns.index(crd1[0]) - columns.index(crd2[0]))
    if  v == 1:
        return abs(rows.index(crd1[1]) - rows.index(crd2[1])) == 2
    elif v == 2:
        return abs(rows.index(crd1[1]) - rows.index(crd2[1])) == 1
    return False

def check_line(sqr1 : str,sqr2 : str) -> bool:
    c1 = sqr1[0]
    c2 = sqr2[0]
    r1 = int(sqr1[1])
    r2 = int(sqr2[1])
    if r1 == r2:
        i1 = columns.index(c1)
        i2 = columns.index(c2)
        return all(pieces[columns[i]+str(r1)] == '' for i in range(min(i1,i2)+1,max(i1,i2)))
    elif c1 == c2:
        return all(pieces[c1+str(i)] == '' for i in range(min(r1,r2)+1,max(r1,r2)))
    return False

def check_diagonal(sqr1 : str,sqr2 : str) -> bool:
    c1 = columns.index(sqr1[0])
    c2 = columns.index(sqr2[0])
    r1 = int(sqr1[1])
    r2 = int(sqr2[1])
    if abs(c1 - c2) == abs(r1 - r2):
        if c1>c2 and r1>r2 or c2>c1 and r2>r1:
           min_c = min(c1,c2)
           min_r = min(r1,r2)
           return all(pieces[columns[min_c+i] + str(min_r + i)] == '' for i in range(1,abs(c1-c2)))

        elif c1 > c2 and r2 > r1:
            return all(pieces[columns[c2+i]+str(r2-i)] == '' for i in range(1,c1-c2))

        return all(pieces[columns[c2-i] + str(r2+i)] == '' for i in range(1,c2-c1))
    return False 

def update_pieces(frm : str, to : str, piece_type : str):
    pieces[frm] = ''
    pieces[to] = piece_type 

def source_of_move(move : str , turn : int) -> tuple:
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
                source = c + next(str(i) for i in range(r,0,-1) if pieces[c+str(i)] == p)
            else:
                source = c + next(str(i) for i in range(r,9) if pieces[c+str(i)] == p) 
        # Capturing pawn e.g. ed5
        elif len(move) == 3:
            if pieces[move[-2:]] != '': 
                if turn == 0:
                    source = move[0] + str(r-1)
                else:
                    source = move[0] + str(r+1)
            # En Passant 
            else:
                if turn == 0:
                    next_pawn = c + str(r - 1)
                else:
                    next_pawn = c + str(r + 1)
                clear(pixels_from_square(next_pawn))
                pieces[next_pawn] = ''
                source = move[0] + next_pawn[-1]
   
    elif move[0] == 'K':
        p = 'wk' if turn == 0 else 'bk'
        source = next(sq for sq,pt in pieces.items() if pt == p)

    elif move[0] == 'B':
        p = 'wb' if turn == 0 else 'bb'
        if len(move) == 3:
            source = next(sq for sq,pt in pieces.items() if pt == p and check_diagonal(sq,to))   
        else:
            indicator = move[1]
            source = next(sq for sq,pt in pieces.items() if pt==p and indicator in sq and check_diagonal(sq,to))

    elif move[0] == 'R':
        p = 'wr' if turn == 0 else 'br'
        # e.g. Ra3
        if len(move) == 3:
            try:
                source = c + next(row for row in rows if pieces[c + str(row)] == p and check_line(c+str(row),to))
            except:
                source = next(col for col in columns if pieces[col + str(r)] == p and check_line(col+str(r),to)) + str(r) 
        # e.g. Raa3
        else:
            indicator = move[1]
            if indicator in columns:
                source = indicator + next(row for row in rows if pieces[indicator+row]==p)
            else:
                source = next(col for col in columns if pieces[col+indicator]==p) + indicator

    elif move[0] == 'Q':
        p = 'wq' if turn == 0 else 'bq'
        if len(move) == 3:
            source = next(sq for sq,pt in pieces.items() if pt == p and (check_line(sq,to) or check_diagonal(sq,to)))
        else:
            indicator = move[1]
            source = next(sq for sq,pt in pieces.items() if pt == p and indicator in (move[0],move[1]))

    elif move[0] == 'N':
        p = 'wn' if turn == 0 else 'bn'
        if len(move) == 3:
            source = next(sq for sq,pt in pieces.items() if pt == p and check_knight_move(sq,to))
        else:
            indicator = move[1]
            source = next(sq for sq,pt in pieces.items() if pt == p and indicator in sq and check_knight_move(sq,to))

    update_pieces(source,to,p)
    return pixels_from_square(source)

def create_gif(file_name : str, out_name : str, duration : float = 0.5):
    global pieces
    pieces = {'a8' : 'br','b8' : 'bn','c8' : 'bb','d8' : 'bq','e8' : 'bk','f8' : 'bb','g8' : 'bn','h8' : 'br',
              'a7' : 'bp','b7' : 'bp','c7' : 'bp','d7' : 'bp','e7' : 'bp','f7' : 'bp','g7' : 'bp','h7' : 'bp',
              'a6' : '','b6' : '','c6' : '','d6' : '','e6' : '','f6' : '','g6' : '','h6' : '',
              'a5' : '','b5' : '','c5' : '','d5' : '','e5' : '','f5' : '','g5' : '','h5' : '',
              'a4' : '','b4' : '','c4' : '','d4' : '','e4' : '','f4' : '','g4' : '','h4' : '',
              'a3' : '','b3' : '','c3' : '','d3' : '','e3' : '','f3' : '','g3' : '','h3' : '',
              'a2' : 'wp','b2' : 'wp','c2' : 'wp','d2' : 'wp','e2' : 'wp','f2' : 'wp','g2' : 'wp','h2' : 'wp',
              'a1' : 'wr','b1' : 'wn','c1' : 'wb','d1' : 'wq','e1' : 'wk','f1' : 'wb','g1' : 'wn','h1' : 'wr'}
    
    images = [np.array(board)]
    moves = get_moves(file_name)
    
    for i in range(len(moves)):
        update(moves[i] , i % 2)
        images.append(np.array(board))
    images.append(np.array(board))

    imageio.mimsave(f'gifs/{out_name}',images,duration=duration)

if __name__ == '__main__':
    import glob

    print('pgn2gif')
    for pgn in glob.glob('*.pgn'):
        name = os.path.basename(pgn)[:-4] + '.gif' 
        if name in os.listdir('gifs/'):
            continue
        else:
            print('Creating ' + name + '...')
            create_gif(pgn,name)
            print('Done ')


