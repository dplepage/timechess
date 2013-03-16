from board import ChessBoard, ChessPieces

def make_chess():
    '''Generate a starting board for chess.'''
    b = ChessBoard(size=(8,8))
    # Set up a chess board
    for i in range(8):
        b[i, 1] = ChessPieces.create('Pawn', player=0)
        b[i, 6] = ChessPieces.create('Pawn', player=1)
    for i, c in enumerate('RNBQKBNR'):
        b[i, 0] = ChessPieces.create(c, player=0)
        b[i, 7] = ChessPieces.create(c, player=1)
    return b

def make_small_chess():
    '''Generate a starting board for chess.'''
    b = ChessBoard(size=(5,5))
    # Set up a chess board
    for i in range(5):
        b[i, 1] = ChessPieces.create('Pawn', player=0)
        b[i, 3] = ChessPieces.create('Pawn', player=1)
    for i, c in enumerate('NBQKR'):
        b[i, 0] = ChessPieces.create(c, player=0)
        b[i, 4] = ChessPieces.create(c, player=1)
    return b
