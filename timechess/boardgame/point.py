from collections import namedtuple
import string

class Point(namedtuple('Point', ['x', 'y'])):
    '''A subclass of Tuple with different operations.

    Adding/subtracting two Points yields a new one, and so does multiplying by
    a number.

    >>> p1 = Point(1,2)
    >>> p2 = Point(x=4, y=5)
    >>> p1
    Point(x=1, y=2)
    >>> p2
    Point(x=4, y=5)
    >>> (p1+p2*6)*2 + p2
    Point(x=54, y=69)
    >>> Point(0, 0).as_alg()
    'a1'
    >>> Point.from_alg('b3')
    Point(x=1, y=2)
    '''
    def __new__(cls, x, y=None):
        if isinstance(x, (list, tuple)) and y is None:
            x, y = x
        if isinstance(x, basestring) and y is None:
            return Point.from_alg(x)
        return super(Point, cls).__new__(Point, int(x), int(y))

    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def __mul__(self, val):
        return Point(self.x*val, self.y*val)

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))

    def dist(self, other=None, metric="chessboard"):
        if other is None: other = Point(0,0)
        if metric == 'chessboard':
            return max(abs(self.x-other.x), abs(self.y-other.y))
        if metric == 'manhattan':
            return abs(self.x-other.x) + abs(self.y-other.y)
        if metric == 'cartesian':
            return ((self.x-other.x)**2 + (self.y-other.y)**2)**.5
        raise ValueError("Unrecognized metric: {0}".format(metric))

    def rots(self):
        return [self, Point(self.y, -self.x), Point(-self.x, -self.y), Point(-self.y, self.x)]

    def is_white(self):
        '''Return whether this square is white.

        Squares form a checkerboard pattern, with (0,0) being nonwhite.
        '''
        return bool((self.x+self.y)%2)

    # Helper fns for translating between numerical and algebraic coordinates
    @classmethod
    def col_label(cls, x):
        return string.letters[x]

    @classmethod
    def row_label(cls, y):
        return str(y+1)

    def as_alg(self):
        return self.col_label(self.x)+self.row_label(self.y)

    @classmethod
    def from_alg(cls, alg):
        c = alg[0]
        r = int(alg[1:])
        return Point(string.letters.index(c), r-1)

    def __str__(self):
        return self.as_alg()