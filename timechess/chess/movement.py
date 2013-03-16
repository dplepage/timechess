from dfiance import String, Invalid, TypeDictifier

from timechess.boardgame import Point, BasicMove, TemporalInstability
from timechess.boardgame import MoveManager, ChronoErasure
from board import EPState, ChessPieces
from config import AttrDict

class PromotionMove(BasicMove):
    '''A piece moves from a start point to an end point and promotes.
    '''
    field_types = dict(
        promotion = String,
    )
    def __init__(self, piece, start, end, promotion):
        super(PromotionMove, self).__init__(piece, start, end)
        self.promotion = promotion

    def __str__(self):
        start, end = self.alg()
        return u'{2} {0}-{1}, to {3}'.format(start, end, self.piece, self.promotion)

    def __hash__(self):
        return hash((self.start, self.end, self.piece.name, self.piece.player, self.promotion))

class MoveComputer(object):
    def __init__(self, board, player, start):
        self.board = board
        self.player = player
        self.start = start
        self.piece = self.board[self.start]

    def _mv(self, pos):
        return BasicMove(self.piece, self.start, pos)

    def is_enemy(self, pos):
        o = self.board.player(pos)
        return o is not None and o != self.player

    def is_friend(self, pos):
        p = self.board[pos]
        return p is not None and p.player == self.player

    def all_moves(self):
        if not self.piece or self.piece.player != self.player or not self.piece.moveable:
            return set()
        if self.piece.name == 'Pawn':
            return self.pawn_moves()
        if self.piece.name == 'Rook':
            return self.rook_moves()
        if self.piece.name == 'Bishop':
            return self.bishop_moves()
        if self.piece.name == 'Queen':
            return self.bishop_moves().union(self.rook_moves())
        if self.piece.name == 'King':
            return self.king_moves()
        if self.piece.name == 'Knight':
            return self.knight_moves()
        raise Exception("Unknown piece: {0}".format(self.piece))

    def knight_moves(self):
        moves = set()
        for d in Point(1,2).rots() + Point(2,1).rots():
            p = self.start+d
            if p in self.board and self.board.player(p) != self.player:
                moves.add(self._mv(p))
        return moves

    def pawn_moves(self):
        moves = set()
        if self.player == 0:
            fwd = Point(0,1)
            start_row = 1
            end_row = self.board.nrows()-1
        else:
            fwd = Point(0,-1)
            start_row = self.board.nrows()-2
            end_row = 0
        front = self.start + fwd
        if front not in self.board:
            return set() # Can't move a pawn in the last row!
        if not self.board[front]:
            moves.add(self._mv(front))
            if self.start[1] == start_row and not self.board[front+fwd]:
                moves.add(self._mv(front+fwd))
        for p in [front+Point(1,0), front+Point(-1,0)]:
            is_ep = p == self.board.ep.capture_point and self.is_enemy(self.board.ep.target)
            if self.is_enemy(p) or is_ep:
                moves.add(self._mv(p))
        for move in list(moves):
            if move.end[1] == end_row:
                moves.remove(move)
                for promotion in 'QNRB':
                    moves.add(PromotionMove(move.piece, move.start, move.end, promotion))
                # TODO add promotion move here
        return moves

    def king_moves(self):
        moves = self.bishop_moves(limit=1).union(self.rook_moves(limit=1))
        if self.player == 0 and self.start != (4,0):
            return moves
        if self.player == 1 and self.start != (4,7):
            return moves
        def clear(*spaces):
            return not any(self.board[x] for x in spaces)
        def rook(space):
            piece = self.board[space]
            return piece and piece.name == 'Rook' and piece.player == self.player
        cstate = self.board.castling[self.player]
        if self.player == 0:
            if not cstate.kingside and clear('f1', 'g1') and rook('h1'):
                moves.add(self._mv(Point.from_alg('g1')))
            if not cstate.queenside and clear('b1','c1','d1') and rook('a1'):
                moves.add(self._mv(Point.from_alg('c1')))
        elif self.player == 1:
            if not cstate.kingside and clear('f8', 'g8') and rook('h8'):
                moves.add(self._mv(Point.from_alg('g8')))
            if not cstate.queenside and clear('b8','c8','d8') and rook('a8'):
                moves.add(self._mv(Point.from_alg('c8')))
        return moves

    def rook_moves(self, limit=8, can_capture=True):
        return self.multi_rider(Point(0,1).rots(), limit, can_capture)

    def bishop_moves(self, limit=8, can_capture=True):
        return self.multi_rider(Point(1,1).rots(), limit, can_capture)

    def multi_rider(self, dirs, limit=8, can_capture=True):
        return set.union(*[self.rider_moves(d, limit, can_capture) for d in dirs])

    def rider_moves(self, dir, limit=8, can_capture=True):
        '''
        >>> from chess_board import ChessBoard
        >>> board = ChessBoard()
        '''
        dir = Point(*dir)
        moves = set()
        for i in range(1, limit+1):
            p = (self.start + dir*i)
            if p not in self.board:
                break
            other = self.board[p]
            if other:
                if other.player != self.player and can_capture:
                    moves.add(self._mv(p))
                break
            moves.add(self._mv(p))
        return moves

class AttrDictType(TypeDictifier):
    type=AttrDict
    allowed_types=dict

class ChessManager(MoveManager):
    field_types = dict(
        config = AttrDictType(),
    )
    def __init__(self, config):
        self.config = config

    def get_moves(self, board, player = None, start = None):
        if start is None:
            moves = set()
            for ind in board.iterinds():
                moves |= self.get_moves(board, player, start=ind)
            return moves
        if player is None and not board[start]:
            return []
        elif player is None:
            player = board[start].player
        return MoveComputer(board, player, start).all_moves()

    def is_legal(self, board, move):
        p = board[move.start]
        if not p:
            return False
        if p.player != move.player:
            return False
        c = MoveComputer(board, move.player, move.start)
        return move in c.all_moves()

    def apply(self, board, move):
        """Apply this move to a board, returning a new board.

        In the future, this is where checking that it's a valid move will go.
        """
        piece = board[move.start]
        if not piece: # No piece = no move
            return False
        move = self.degrade(board, move)
        if not move:
            return False
        board = board.copy()
        piece = board[move.start]
        # En Passant: If a pawn moves orthogonally two spaces, then the
        # middle space is marked as the En Passant capture space. Note that
        # this includes moving two spaces due to degradation.
        if piece.name == "Pawn":
            if move.end == board.ep.capture_point:
                board[board.ep.target] = None
            if abs(move.start-move.end) in [Point(0,2), Point(2,0)]:
                target = move.start + (move.end-move.start)*.5
                board.ep = EPState(target, move.end)
            else:
                board.ep = EPState()
        else:
            board.ep = EPState()
        # Castling: If a King moves two spaces, it swaps with the nearest Rook
        if piece.name == 'King' and abs(move.start-move.end) in [Point(2,0), Point(0,2)]:
            delta = (move.end-move.start)*.5
            for i in range(8):
                new_piece = board[move.start + delta*i]
                if not new_piece: continue
                if new_piece.name == 'Rook':
                    board[move.start+delta*i] = None
                    board[move.start+delta] = new_piece
                    break
        # Castling: When rooks/kings move they can't castle again
        if piece.name == 'King':
            board.castling[piece.player].clear()
        if piece.name == 'Rook':
            if move.start == (0,0):
                board.castling[0].queenside = True
            elif move.start == (7,0):
                board.castling[0].kingside = True
            elif move.start == (0,7):
                board.castling[1].queenside = True
            elif move.start == (7,7):
                board.castling[1].kingside = True
        # Movability
        if self.config.require_enemy_movement:
            piece.moveable = False
            for ind, piece2 in board.itercells():
                if piece2 and piece2.player != move.player:
                    piece2.moveable = True
        if self.config.require_friendly_movement:
            for ind, piece2 in board.itercells():
                if piece2 and piece2.player == move.player:
                    piece2.moveable = True
            piece.moveable = False
        if piece.name == 'Pawn':
            capture_erases = self.config['pawn_capture_erases']
        else:
            capture_erases = self.config['nonpawn_capture_erases']
        hardy_pawns = self.config.get('pawns_resist_erasure')
        if board[move.end] and capture_erases:
            if not hardy_pawns or board[move.end].name != 'Pawn':
                raise ChronoErasure(board[move.end].uid)
        board[move.end] = board[move.start]
        board[move.start] = None
        # Promotion
        if isinstance(move, PromotionMove):
            piece.short = move.promotion
            piece.name = ChessPieces.names[move.promotion]
        return board

    def degrade(self, board, move):
        '''Given an existing move, construct the corresponding degradation.

        For example, if the move is "White pawn f3-f4", but the piece at f3 is
        a white queen, this will return "White queen f3-f4".

        Likewise if the move is "White queen e1-g1", but the piece at f2 is a
        white king, the new move will be "White castles kingside" (assuming
        white can do so).

        Returns None if no degradation exists, for example because there is no
        piece at the start at all.
        '''
        piece = board[move.start]
        if not piece:
            return None
        if self.config.degrade_require_same_player and piece.player != move.player:
            return None
        if self.config.degrade_require_same_piece and piece.name != move.piece.name:
            return None
        if not piece.moveable:
            return None
        # Convert non-basic moves to basic moves except when it's the same piece
        if piece.name != move.piece.name:
            move = BasicMove(piece, move.start, move.end)
        else:
            move = BasicMove.undictify(move.dictify())
            move.piece = piece
        if self.config.degrade_require_legal_move and not self.is_legal(board, move):
            return None
        if not self.config.degrade_allow_self_capture and board.player(move.end) == piece.player:
            return None
        return move
