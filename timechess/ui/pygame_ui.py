#/usr/bin/env python

import math
import os.path

import pygame

import timechess
from timechess.boardgame import Point
from ascii_ui import AsciiUI
from base_ui import AmbiguousMove

class ImgLoader(object):
    def __init__(self, image_map=None, root=None):
        self.image_map = image_map or {}
        if not root:
            root = timechess.root
        self.root = root

    def path_for_name(self, image_name):
        return os.path.join(self.root, "images", "png", image_name)

    def path(self, piece):
        name = "Chess_"+piece.short.lower()+"ld"[piece.player]+"t45.png"
        return self.path_for_name(name)

    def img(self, piece):
        path = self.path(piece)
        if path not in self.image_map:
            self.image_map[path] = pygame.image.load(path)
        return self.image_map[path]

class PyGameUI(AsciiUI):
    def __init__(self, game):
        super(PyGameUI, self).__init__(game)
        pygame.init()
        self.image_loader = ImgLoader()
        self.screen = pygame.display.set_mode((600, 480), 1)
        pygame.display.set_caption("Time Chess")
        self.last_cmd = ''
        self.font = pygame.font.Font(pygame.font.get_default_font(), 18)
        # if ambiguity is not None, we're in the process of resolving an
        # ambiguous move (e.g. a pawn promotion)
        self.ambiguity = None

    def screen2board(self, x, y):
        '''Convert screen coordinates to a board cell.'''
        return Point(x//60, 7-(y//60))

    def center_of(self, point):
        '''Find the center of a board cell in screen coords.'''
        x, y = point
        return x*60+30, (7-y)*60+30

    def ul_of(self, point):
        '''Find the upper-left corner of a board cell in screen coords.'''
        x, y = point
        return x*60, (7-y)*60

    def do_command(self, cmd):
        self.last_cmd = cmd
        return super(PyGameUI, self).do_command(cmd)

    def on_click(self, event):
        if self.ambiguity:
            for i, move in enumerate(self.ambiguity.moves):
                rect = pygame.Rect(0, i*40, 150, 30)
                if rect.collidepoint(event.pos):
                    self.move_to(self.ambiguity.moves[i], change=self.ambiguity.change)
                    self.ambiguity = None
                    break
        else:
            mousePos = self.screen2board(*event.pos)
            # Check bounds
            if mousePos not in self.game.start_board:
                return
            if self.selected_square == mousePos:
                # If you click the selected square, deselect it.
                self.deselect()
            elif not self.selected_square:
                # If there's no selection, set one iff there's a piece
                if self.curr_board()[mousePos]:
                    self.select(mousePos)
            else:
                # There is a selection, and it's not here
                try:
                    self.move_to(mousePos, change=pygame.key.get_mods() & pygame.KMOD_SHIFT)
                except AmbiguousMove, e:
                    self.ambiguity = e

    def arrow(self, start, end, color=(0,0,0), width=6):
        s, e = self.center_of(start), self.center_of(end)
        pygame.draw.line(self.screen, color, s, e, width)
        pygame.draw.circle(self.screen, color, s, width)
        arrow = pygame.Surface((20,20))
        arrow.fill((255,255,255))
        pygame.draw.line(arrow, color, (0,0), (10,10), width)
        pygame.draw.line(arrow, color, (0,20), (10,10), width)
        arrow.set_colorkey((255,255,255))
        angle=math.atan2(-(s[1]-e[1]), s[0]-e[0])
        angle=math.degrees(angle)
        def drawAng(angle, pos):
            nar=pygame.transform.rotate(arrow,angle)
            nrect=nar.get_rect(center=pos)
            self.screen.blit(nar, nrect)
        drawAng(angle+180, e)

    def highlight(self, point, color=(255, 255, 0), width=4):
        x, y = self.center_of(point)
        rect = pygame.Rect(x-30, y-30, 60, 60)
        pygame.draw.rect(self.screen, color, rect, width)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            key = event.key
            char = event.unicode.lower()
            if key == pygame.K_ESCAPE or char == 'q':
                self.running = False
            elif key in [pygame.K_LEFT, pygame.K_UP] or char == 'b':
                self.back()
            elif key in [pygame.K_RIGHT, pygame.K_DOWN] or char == 'f':
                self.fwd()
            elif char == 'u':
                self.undo()
            elif char == 'i':
                self.interact()
            else:
                print key
        elif event.type == pygame.MOUSEMOTION:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_click(event)

    def draw(self):
        if self.ambiguity:
            self.draw_ambiguity()
        else:
            self.draw_board()
        pygame.display.flip()

    def draw_board(self):
        board = self.curr_board()
        shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
        pygame.display.set_caption('ChessBoard Client')
        for ind, piece in board.itercells():
            if ind.is_white():
                color = (255, 206, 158)
            else:
                color = (209, 139, 71)
            piece = board[ind]
            x, y = self.ul_of(ind)
            self.screen.fill(color, pygame.Rect(x, y, 60, 60))
            if piece:
                image = self.image_loader.img(piece)
                self.screen.blit(image, (x, y))
        # Draw moves
        self.screen.fill((0,0,0), pygame.Rect(480,0,120,480))
        pos = 2
        nmoves = len(self.game.moves)
        if self.turn >= nmoves-9:
            start = max(0, nmoves-19)
        else:
            start = max(0, self.turn-9)
        end = min(nmoves, start+19)
        for i, move in enumerate(self.game.moves[start:end]):
            background = (0,0,0)
            if move.valid:
                color = (255, 255, 255)
            else:
                color = (255, 0, 0)
            if i+start == self.turn:
                if shift:
                    rect = pygame.Rect(480, pos-5, 120, 25)
                    background = (255, 255, 0)
                    color = (0,0,0)
                else:
                    rect = pygame.Rect(480, pos-5, 120, 4)
                self.screen.fill((255,255,0), rect)
            text = "WB"[move.player] + str(move.start)+"-"+str(move.end)
            msg = self.font.render(text, True, color, background)
            self.screen.blit(msg, (482, pos))
            pos += 5 + msg.get_bounding_rect().h
        if len(self.game.moves) == self.turn:
            self.screen.fill((255,255,0), pygame.Rect(480, pos-5, 120, 4))
        if self.selected_square:
            self.highlight(self.selected_square)
            for move in self.available_moves:
                self.highlight(move.end, (0, 0, 255))
        if self.turn < len(self.game.moves):
            move = self.game.moves[self.turn]
            color = [(0,0,255), (0,255,0)][move.valid]
            self.arrow(move.start, move.end, color)

    def draw_ambiguity(self):
        pygame.display.set_caption('ChessBoard Client')
        for i, move in enumerate(self.ambiguity.moves):
            rect = pygame.Rect(0, i*40, 150, 30)
            self.screen.fill((0,0,0), rect)
            msg = self.font.render(str(move), True, (255,255,255), (0,0,0))
            self.screen.blit(msg, (5, i*40+5))

    def main_loop(self):
        clock = pygame.time.Clock()
        self.running = True
        while self.running:
            clock.tick(30)
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()

UIClass = PyGameUI