from dfiance import List, Polymorph, Invalid

from timechess.boardgame import Game, BasicMove

from board import ChessBoard
from movement import ChessManager, PromotionMove

class DictPolymorph(Polymorph):
    def __init__(self, mapping, poly_on="_polymorphic_type"):
        super(DictPolymorph, self).__init__(mapping)
        self.poly_on = poly_on

    def dictify(self, value, **kwargs):
        name, d = super(DictPolymorph, self).dictify(value, **kwargs)
        d[self.poly_on] = name
        return d

    def undictify(self, value, **kwargs):
        if self.poly_on not in value:
            raise Invalid("type_error")
        name = value.pop(self.poly_on)
        return super(DictPolymorph, self).undictify((name, value), **kwargs)

ChessMove = DictPolymorph(dict(
        basic = BasicMove,
        promo = PromotionMove,
    ))

class ChessGame(Game):
    field_types = dict(
        start_board = ChessBoard.dfier(),
        mgr = ChessManager.dfier(),
        moves = List(ChessMove)
    )
