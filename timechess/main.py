'''Time Chess standalone app

Run this with e.g. `python -m timechess.main pygame`

You can use 'pygame', 'ascii', or 'curses' as the argument; it defaults to
'pygame'.

'''


from timechess.chess import ChessGame, make_config, ChessBoard, boards
from timechess.chess import ChessManager

uis = {
    'pygame': 'PyGameUI',
    'ascii': 'AsciiUI',
    'curses': 'CursesUI',
}

def main(*args):
    if len(args) < 2:
        ui = 'pygame'
    else:
        ui = args[1]
    mname = "{0}_ui".format(ui)
    module = __import__("timechess.ui.{0}".format(mname))
    module = getattr(getattr(module, 'ui'), mname)
    cls = getattr(module, uis[ui])
    config = make_config()
    start_board = boards.make_chess()
    mgr = ChessManager(config)
    # start_board = boards.make_small_chess()
    game = ChessGame(start_board, mgr)
    cls.run(game)

if __name__ == '__main__':
    import sys
    main(*sys.argv)
