from dfiance import SchemaObj, Boolean, List

from timechess.boardgame import Board, Piece, PieceRegistry, PointType

ChessPieces = PieceRegistry(dict(
    Pawn = 'p',
    Knight = 'N',
    Bishop = 'B',
    Rook = 'R',
    Queen = 'Q',
    King = 'K'
))

class CastleState(SchemaObj):
    '''Indicates whether a player can castle.

    kingside is True if the kingside rook or the king has moved.
    queenside is True if the queenside rook or the king has moved.
    '''
    field_types = dict(
        kingside = Boolean(),
        queenside = Boolean(),
    )
    def __init__(self, kingside=False, queenside=False):
        self.kingside = kingside
        self.queenside = queenside

    def clear(self):
        self.kingside = self.queenside = True

class EPState(SchemaObj):
    '''Indicates an En Passant capture point'''
    field_types = dict(
        capture_point = PointType(),
        target = PointType(),
    )
    def __init__(self, capture_point=None, target=None):
        self.capture_point=capture_point
        self.target = target

class ChessBoard(Board):
    '''A Chess Board, plus castling state and legal En Passant capture point.'''
    field_types = dict(
        castling = List(CastleState),
        ep = EPState.dfier(),
    )

    def __init__(self, cells=None, wcstate=None, bcstate=None, ep=None, size=None):
        super(ChessBoard, self).__init__(cells, size)
        self.castling = [wcstate or CastleState(), bcstate or CastleState()]
        self.ep = ep or EPState()
