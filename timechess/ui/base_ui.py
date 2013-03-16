import copy

from timechess.boardgame import Move
from timechess.chess import ChessGame, ChessBoard

class AmbiguousMove(Exception):
    '''Raised when move_to finds multiple possible moves'''
    def __init__(self, moves, change):
        self.moves = moves
        self.change = change

class BaseUI(object):
    '''Abstract UI. Stores a ChessGame plus the currently-viewed turn.

    Has useful fns for moving around in time and adding/changing moves.
    '''
    def __init__(self, game, history=None, turn=0):
        self.game = game
        self.game_type = type(game)
        self.history = history or []
        if not self.history:
            self._save_hist()
        self.turn = turn
        self.last_msg = ""
        # Track a currently selected square and all moves possible from it
        self.selected_square = None
        self.available_moves = []

    def _save_hist(self):
        self.history.append(self.game.dictify())

    def curr_board(self):
        '''Return the board at the current turn'''
        return self.game.boards[self.turn]

    def undo(self):
        if len(self.history) == 1:
            self.last_msg="Nothing to undo."
            return False
        self.history.pop()
        self.game = self.game_type.undictify(self.history[-1])
        self.back()
        self.last_msg = "Ok."
        return True

    def interact(self):
        '''Invoke the danutils command line, if present.'''
        try:
            from danutils.do.interact import doit
            self.last_msg = "Ok."
            return True
        except ImportError:
            self.last_msg = "danutils is not installed."
            return False

    def back(self):
        '''Go back a turn'''
        if self.turn == 0:
            self.last_msg = "At start of game."
            return False
        self.turn -= 1
        if self.selected_square:
            self.select(self.selected_square)
        self.last_msg = "Ok."
        return True

    def fwd(self):
        '''Go forward a turn'''
        if self.turn == len(self.game.moves):
            self.last_msg = "At end of game."
            return False
        self.turn += 1
        if self.selected_square:
            self.select(self.selected_square)
        self.last_msg = "Ok."
        return True

    def goto_turn(self, turn):
        if turn < 0 or turn > len(self.game.moves):
            self.last_msg = "Can't jump to turn {0}.".format(turn)
            return False
        self.turn = turn
        if self.selected_square:
            self.select(self.selected_square)
        self.last_msg = "Ok."
        return True

    def select(self, square):
        '''Select a square, storing moves from that square in self.moves'''
        self.selected_square = square
        self.available_moves = self.game.get_moves(self.turn, None, square)

    def deselect(self):
        self.selected_square = None
        self.available_moves = []

    def filter_moves(self, endpoint):
        '''Return all selected moves that end at endpoint'''
        moves = []
        for move in self.available_moves:
            if move.end == endpoint:
                moves.append(move)
        return moves

    def move_to(self, endpoint_or_move, change=False):
        if isinstance(endpoint_or_move, Move):
            move = endpoint_or_move
        else:
            endpoint = endpoint_or_move
            if not self.selected_square:
                self.last_msg = "No start point selected."
                return False
            moves = self.filter_moves(endpoint)
            if not moves:
                return
            if len(moves) == 1:
                move = moves[0]
            else:
                raise AmbiguousMove(moves, change)
        if change:
            self.change_move(move)
        else:
            self.insert_move(move)
        self.deselect()
        return True

    def insert_move(self, move):
        '''Add a move at the current turn'''
        if self.game.insert_move(move, self.turn):
            self._save_hist()
            self.fwd()
            self.last_msg = "Ok."
            return True
        self.last_msg = "Illegal move."
        return False

    def change_move(self, move):
        '''Change the move at the current turn'''
        if self.game.change_move(move, self.turn):
            self._save_hist()
            self.fwd()
            self.last_msg = "Ok."
            return True
        self.last_msg = "Illegal move."
        return False

    def main_loop(self):
        raise NotImplementedError()

    @classmethod
    def run(cls, game):
        cls(game).main_loop()
