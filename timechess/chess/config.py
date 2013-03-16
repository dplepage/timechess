class AttrDict(dict):
    """A dictionary whose keys can be accessed/set by attribute.

    >>> x = AttrDict({'foo':1, 'bar':12, 'baz':123})
    >>> sorted(x.items())
    [('bar', 12), ('baz', 123), ('foo', 1)]
    >>> x.foo
    1
    >>> x.bar
    12
    >>> x.baz = 99
    >>> x['baz']
    99
    >>> x.spam = "hello"
    >>> x['spam'], x.spam
    ('hello', 'hello')
    """
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def copy(self):
        return AttrDict(dict.copy(self))

default_config = AttrDict(
    # Only degrade if the new piece is owned by the move's original maker
    degrade_require_same_player = False,
    # Only degrade if the new piece is the same piece type as the original
    degrade_require_same_piece = False,
    # Only degrade if the new move is legal for the piece that's there
    degrade_require_legal_move = True,
    # Degrade even if it causes a player to capture their own piece
    # (this can only happen if require_legal_move is False)
    degrade_allow_self_capture = False,
    # You can't move a piece twice in a row without an enemy piece moving
    require_enemy_movement = False,
    # You can't move a piece twice in a row without moving another piece
    require_friendly_movement = False,
    # ^ Note that if the above are both true, a piece becomes movable after any
    # piece on either side moves.
    # Capturing a piece with a non-pawn removes it from history
    nonpawn_capture_erases = True,
    # Capturing a piece with a pawn removes it from history
    pawn_capture_erases = False,
    # Pawns are immune to erasure
    pawns_resist_erasure = False,
)

def make_config(**kwargs):
    d = default_config.copy()
    d.update(kwargs)
    return d

def conf_opts():
    return default_config.copy()

if __name__ == '__main__':
    import doctest
    doctest.testmod()