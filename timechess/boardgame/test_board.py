import unittest

from board import Board
from object_types import Piece

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board['a1'] = Piece(player=0, name="Pawn", short="P")
