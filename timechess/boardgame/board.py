from dfiance import SchemaObj, List, Field

from datatypes import Point, Piece

pieceGrid = List(List(Field(Piece)))

class Board(SchemaObj):
    '''An abstract game board.'''
    field_types = dict(
        cells = pieceGrid
    )

    def __init__(self, cells=None, size=None):
        if cells is None:
            if size is None:
                size = Point(8,8)
            else:
                size = Point(size)
            cells = [[None for i in range(size.x)] for i in range(size.y)]
        self.cells = pieceGrid.undictify(cells)

    def __getitem__(self, coords):
        p = Point(coords)
        if p not in self:
            return None
        return self.cells[p.x][p.y]

    def __setitem__(self, coords, item):
        p = Point(coords)
        self.cells[p.x][p.y] = item

    def __contains__(self, coords):
        p = Point(coords)
        if p.x >= self.ncols() or p.x < 0:
            return False
        if p.y >= self.nrows() or p.y < 0:
            return False
        return True

    def iterinds(self):
        '''Iterate over all indices'''
        for c in range(self.ncols()):
            for r in range(self.nrows()):
                yield Point(c,r)

    def itercells(self, include_empty=True):
        '''Iterate over all (index, piece) pairs.

        Includes empty cells as (index, None)
        '''
        for ind in self.iterinds():
            if include_empty or self[ind] is not None:
                yield ind, self[ind]

    def player(self, pos):
        '''Get the player of the piece at pos, or None if empty.'''
        p = self[pos]
        if not p:
            return None
        return p.player

    def name(self, pos):
        '''Get the name of the piece at pos, or None if empty.'''
        p = self[pos]
        if not p:
            return None
        return p.name

    def copy(self):
        '''Clone a Board.'''
        return self.dfier().undictify(self.dictify())

    def ncols(self):
        return len(self.cells)

    def nrows(self):
        return len(self.cells[0])

    def ascii(self, labels=True):
        '''Print the board as ASCII.'''
        ncols = len(self.cells)
        nrows = len(self.cells[0])
        sep = '+' + '--+'*ncols
        s = [sep]
        for row in range(nrows-1,-1,-1):
            line = ['|']
            for col in range(ncols):
                piece = self[col, row]
                if piece is None:
                    line.append("  |")
                else:
                    line.append(piece.ascii() + '|')
            s.append(''.join(line))
            s.append(sep)
        if labels:
            col_label = '  '.join(Point.col_label(i) for i in range(ncols))
            col_label = '   ' + col_label
            for i in range(len(s)):
                label = ' ' if not i%2 else Point.row_label(nrows-1-i//2)
                s[i] = (label+' '+s[i]+' '+label).rstrip()
            s.insert(0, col_label)
            s.append(col_label)
        return '\n'.join(s)
