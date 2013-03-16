import curses
import curses.wrapper

from ascii_ui import AsciiUI

def putblock(win, x, y, text, attrs=0):
    try:
        for i, line in enumerate(text.splitlines()):
            win.addstr(x+i, y, line, attrs)
    except Exception, e:
        raise Exception("Failed to print: " + `text`+"\n   "+str(e))

class CursesUI(AsciiUI):
    def __init__(self, win, game):
        super(CursesUI, self).__init__(game)
        self.win = win
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    def putblock(self, x, y, text, attrs=0):
        putblock(self.win, x, y, text, attrs)

    def draw_moves(self, row, col):
        for i, move in enumerate(self.game.moves):
            color = curses.color_pair(1-move.valid)
            if i == self.turn:
                color |= curses.A_REVERSE
            text = str(move)
            self.putblock(row+i, col, text, color)
        if self.turn == len(self.game.moves):
            self.putblock(row+self.turn, col, '     ', curses.A_REVERSE)

    def redraw(self):
        self.win.clear()
        self.rows, self.cols = self.win.getmaxyx()
        a = self.curr_board().ascii()
        width = len(a.splitlines()[0])
        height = len(a.splitlines())
        rstart = self.rows/2-height/2
        cstart = self.cols/2-width/2-1
        self.putblock(rstart, cstart, a)
        self.putblock(self.rows-2, 0, " " + self.last_msg)
        self.putblock(self.rows-1, 0, ":>"+' '*21)
        self.draw_moves(0,0)
        self.win.refresh()

    def getcmd(self):
        curses.echo()
        curses.curs_set(1)
        x = self.win.getstr(self.rows-1, 3, 20)
        curses.noecho()
        curses.curs_set(0)
        return x.strip()

    @classmethod
    def run(cls, game):
        x = lambda stdscr: cls(stdscr, game).main_loop()
        curses.wrapper(x)

UIClass = CursesUI