from point import Point
from dfiance import SchemaObj, TypeDictifier, String, Boolean, Int, Field

class Piece(SchemaObj):
    '''Abstract game piece.

    name is a string indicating which piece this is.
    player is an integer, or None for unowned pieces.
    short is a 1-character representation of the piece.

    player must be set on init; name and short can be provided by init or by
    subclassing.

    >>> p = Piece(player=0, name="Pawn", short="P")
    >>> print p
    WP
    '''
    field_types = dict(
        name = Field(String(), not_none=True),
        short = Field(String(), not_none=True),
        moveable = Field(Boolean(), not_none=True),
        player = Field(Int(), not_none=True),
        uid = Field(Int(), not_none=True),
    )
    def __init__(self, player, name=None, short=None, uid=None):
        self.player = player
        self.name = name or self.name
        self.short = short or self.short
        self.moveable = True
        self.uid = uid

    def ascii(self):
        return 'WB'[self.player]+self.short

    def __str__(self):
        return self.ascii()


class PieceRegistry(object):
    '''A registry for creating new pieces.'''
    def __init__(self, short_map, piece_class=Piece):
        self.shorts = short_map
        self.names = {short:name for (name, short) in self.shorts.items()}
        self.piece_class = piece_class
        self.next_id = 0

    def create(self, id, **kwargs):
        if id in self.shorts:
            name = id
            short = self.shorts[id]
        elif id in self.names:
            short = id
            name = self.names[id]
        else:
            raise KeyError(id)
        uid = self.next_id
        self.next_id += 1
        return self.piece_class(name=name, short=short, uid=uid, **kwargs)

class Move(SchemaObj):
    '''Abstract base class for all moves.

    Moves are just data records - they don't actually do anything useful.
    '''
    field_types = dict(
        valid = Boolean(),
    )

class PointType(TypeDictifier):
    type = Point
    allowed_types = (Point, list, tuple)

class BasicMove(Move):
    '''A piece moves from a start point to an end point.

    >>> p = Piece(player=0, name="Pawn", short="P")
    >>> b = BasicMove(p, 'a2', 'a4')
    >>> b
    <BasicMove: WP a2-a4>
    >>> b.player
    0
    '''
    field_types = dict(
        start = PointType(),
        end = PointType(),
        piece = Piece.dfier(),
    )
    def __init__(self, piece, start, end):
        self.piece = piece
        self.start = Point(start)
        self.end = Point(end)
        self.valid = True

    @property
    def player(self):
        return self.piece.player

    def endpoints(self):
        '''Return self.start and self.end

        >>> b = BasicMove(None, 'a1', 'a3')
        >>> b.endpoints()
        (Point(x=0, y=0), Point(x=0, y=2))
        '''
        return self.start, self.end

    def alg(self):
        '''Return self.start, self.end as algebraic positions.

        >>> b = BasicMove(None, 'a1', 'a3')
        >>> b.alg()
        ['a1', 'a3']
        '''
        return [self.start.as_alg(), self.end.as_alg()]

    def __str__(self):
        start, end = self.alg()
        return u'{2} {0}-{1}'.format(start, end, self.piece)

    def __repr__(self):
        return u'<{0}: {1}>'.format(type(self).__name__, self)

    def __hash__(self):
        return hash((self.start, self.end, self.piece.name, self.piece.player))

    def __eq__(self, other):
        return hash(self) == hash(other)
