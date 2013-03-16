from dfiance import SchemaObj

class MoveManager(SchemaObj):
    '''Abstract interface for movement managers.'''
    def get_moves(self, board, player = None, start = None):
        """Get the set of legal moves, optionally filtered by player and start.
        """
        raise NotImplementedError()

    def is_legal(self, board, move):
        """Test whether a move is legal for a board"""
        raise NotImplementedError()

    def apply(self, board, move):
        """Apply this move to a board, returning a new board.
        """
        raise NotImplementedError()
