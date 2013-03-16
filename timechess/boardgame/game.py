from dfiance import SchemaObj, List

from datatypes import BasicMove
from board import Board
from movement import MoveManager

class TemporalInstability(Exception):
    '''Exception raised by mgr.apply when history needs to change.
    '''
    pass

class ChronoErasure(TemporalInstability):
    def __init__(self, *uids):
        self.uids = uids

class Game(SchemaObj):
    field_types = dict(
        start_board = Board.dfier(),
        mgr = MoveManager.dfier(),
        moves = List(BasicMove.dfier()),
    )

    def __undictify__(self, value, **kwargs):
        super(Game, self).__undictify__(value, **kwargs)
        self.recompute_boards()

    '''An abstract Game, defined by a starting board and movement manager.'''
    def __init__(self, start_board, move_manager):
        self.start_board = start_board
        self.mgr = move_manager
        self.moves = []
        self.boards = [self.start_board]

    def recompute_boards(self):
        '''Reapply self.moves to self.start_board.'''
        while True:
            self.boards = [self.start_board]
            for move in self.moves:
                try:
                    new_board = self.mgr.apply(self.boards[-1], move)
                except ChronoErasure, e:
                    # Update start board and restart the game
                    for ind, piece in self.start_board.itercells(include_empty=False):
                        if piece.uid in e.uids:
                            self.start_board[ind] = None
                    break
                except TemporalInstability, e:
                    self.mgr.resolve_instability(self, e)
                    break
                move.valid = True
                if new_board is False:
                    move.valid = False
                    new_board = self.boards[-1]
                self.boards.append(new_board)
            else:
                break

    def ascii(self, i=-1, labels=True):
        return self.boards[i].ascii(labels)

    def is_legal(self, turn, move):
        return self.mgr.is_legal(self.boards[turn], move)

    def insert_move(self, move, turn=None):
        if turn is None:
            turn = len(self.moves)
        if self.is_legal(turn, move):
            self.moves.insert(turn, move)
            self.recompute_boards()
            return True
        return False

    def change_move(self, move, turn):
        if turn >= len(self.moves):
            return self.insert_move(move)
        if self.is_legal(turn, move):
            self.moves[turn] = move
            self.recompute_boards()
            return True
        return False

    def get_moves(self, turn, player=None, start=None):
        '''Return possible moves for a turn.'''
        return self.mgr.get_moves(self.boards[turn], player, start)

    def get_state(self):
        return self.start_board, self.moves

    def set_state(self, start_board, moves):
        self.start_board = start_board
        self.moves = moves
        self.recompute_boards()