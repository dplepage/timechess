import re, sys

from timechess.boardgame import BasicMove

from timechess.chess import PromotionMove

from base_ui import BaseUI

class ParseException(Exception):
    pass

move_re = re.compile(
    "(?P<start>[a-z][0-9]+)\s*-\s*(?P<end>[a-z][0-9]+)(:(?P<promo>[QNBR]))?")

def parse_move(move, board):
    match = move_re.match(move.strip())
    if not match:
        raise ParseException("Unable to parse move: {0}".format(move))
    start, end, promo = map(match.group, ['start', 'end', 'promo'])
    piece = board[start]
    if promo:
        return PromotionMove(piece, start, end, promo)
    return BasicMove(piece, start, end)

class AsciiUI(BaseUI):
    def __init__(self, game):
        super(AsciiUI, self).__init__(game)

    def redraw(self):
        print self.curr_board().ascii()
        print self.last_msg
        self.game.undictify(self.game.dictify())
        sys.stdout.flush()

    def do_command(self, cmd):
        if cmd in ['b', 'back']:
            return self.back()
        if cmd in ['f', 'forward']:
            return self.fwd()
        if cmd in ['u', 'undo']:
            return self.undo()
        if cmd in ['i', 'interact']:
            return self.interact()
        try:
            if cmd.startswith('c:'):
                return self.change_move(self.parse_move(cmd[2:]))
            else:
                return self.insert_move(self.parse_move(cmd))
        except ParseException:
            self.last_msg = "Cannot parse command: {0}".format(repr(cmd))
            return False

    def parse_move(self, move, board=None):
        if board is None: board = self.curr_board()
        return parse_move(move, board)

    def getcmd(self):
        return raw_input(":> ")

    def main_loop(self):
        self.redraw()
        while 1:
            sys.stdout.flush()
            cmd = self.getcmd()
            if cmd == 'q':
                break
            else:
                self.do_command(cmd)
            self.redraw()

UIClass = AsciiUI