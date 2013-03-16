============
 Time Chess
============

This is time-travel-themed chess variant where it is not the pieces but the
players who can travel through time.

In essence, you play a game of traditional chess by starting with the
traditional initial board for chess, and alternating with your opponent adding
new moves to the end of a list of moves; the game ends when the list of moves
results in a state where one player's King is capture (or, at least, guaranteed
to be captured).

This variant simply relaxes the restriction "at the end of the list of moves".

Thus, in continuum chess, you have the whole timeline of a game of chess in
front of you, and you and your opponent alternate adding new moves *at any point
in the game's history*.

This of course can lead to invalid moves showing up on the list - they must have
been legal when they were first added, but then the history of the game changed
and now there's a piece in the way, or the piece that should be moving isn't
there, or the space it would be moving to now has a friendly piece in it.

Time Chess deals with this by remembering all the moves that have ever been
added; whenever a new move is added, the engine starts over at the beginning of
the game and applies all the moves in order, skipping any that aren't legal.

Time Chess has three standalone UIs, all of which can be run by::

 python timechess/main.py <ui>

``ascii``
=========

A ludicrously simple ascii UI, mainly for debugging. It prints the board, then
prompts you to type a move. Moves are written as <start>-<end>, eg. ``e2-e4``;
append a colon and piece for promotions, so that ``f7-f8:Q`` means 'Move the
pawn at f7 to f8 and promote it to a queen'. The special commands ``f`` and
``b`` move you forwards and backwards through the time stream; entering a move
will insert at the point where you are. The command 'q' quits.

``curses``
==========

Basically just like ``ascii``, but using curses for a slightly nicer UI.

``pygame``
==========

The preferred way to play locally. It (obviously) requires `PyGame
<http://www.pygame.org/>`_.

``pygame`` is also the default ui - running timechess/main.py will launch the
pygame ui by default.

Google App Engine
=================

In ``/webapp/gae.py``, there's an application for the `Google App Engine
<https://developers.google.com/appengine/>`_ that plays time chess. It's still
pretty bare-bones. You can see it in action on `dplepage.com
<http://www.dplepage.com/timechess/games>`_.

Credits
=======

I had this idea jointly with `Michael Skalak
<http://www.linkedin.com/profile/view?id=202382770>`_, who wrote the initial
prototype in a matter of hours based on a python chess engine by `John Eriksson
<http://arainyday.se>`_

The images used by the PyGame and GAE interfaces are from the Wikimedia Commons
set of `SVG chess pieces
<http://commons.wikimedia.org/wiki/Category:SVG_chess_pieces>`_. They are all
licensed under the `Creative Commons Attribution-Share Alike 3.0 Unported
license <http://creativecommons.org/licenses/by-sa/3.0/deed.en>`_.
