import logging
import uuid, json, datetime, os

now = datetime.datetime.now
from mako.template import Template

from google.appengine.ext import webapp, db

from timechess.chess import ChessGame, make_config, ChessBoard, boards, ChessManager, ChessMove
from timechess.ui.ascii_ui import AsciiUI

def renderTemplate(tname, **vals):
    path = os.path.join(os.path.dirname(__file__), 'templates/%s.html'%tname)
    return Template(open(path).read()).render(**vals)

class GameData(db.Model):
    uid = db.StringProperty()
    state = db.TextProperty()
    timestamp = db.DateTimeProperty()

def new_game(uid=None, conf={}):
    config = make_config(**conf)
    start_board = boards.make_chess()
    mgr = ChessManager(config)
    game = ChessGame(start_board, mgr)
    if not uid:
        uid = str(uuid.uuid4())
    return make_gd(uid, game)

def make_gd(uid, game):
    return GameData(uid=uid, state=json.dumps(game.dictify()), timestamp=now())

def load_game(uid):
    q = GameData.all().filter("uid ==", uid).order("-timestamp")
    game_data = q.get()
    if game_data is None:
        return None, None
    state = json.loads(game_data.state)
    return game_data, ChessGame.undictify(state)

class ChessHandler(webapp.RequestHandler):
    def get(self):
        uid = self.request.get("game_uid")
        if uid:
            return self.redirect("/timechess/game?game_uid={0}".format(uid))
        uids = sorted(set([game.uid for game in GameData.all()]))
        self.response.out.write(renderTemplate("gamelist", uids=uids, config=make_config()))

class NewGameHandler(webapp.RequestHandler):
    def post(self):
        uid=self.request.get('uid')
        if GameData.all().filter("uid ==", uid).count() == 0:
            conf = make_config()
            for key in conf:
                conf[key] = self.request.get(key) == 'true'
            game = new_game(uid=uid, conf=conf)
            game.put()
        return self.redirect("/timechess/game?game_uid={0}".format(uid))

class NewChessHandler(webapp.RequestHandler):
    def get(self):
        uid = self.request.get("game_uid")
        if not uid:
            uids = sorted(set([game.uid for game in GameData.all()]))
            self.response.out.write(renderTemplate("gamelist", uids=uids))
            return
        self.response.out.write(renderTemplate("ajax_game"))
        return

class JSONChessHandler(webapp.RequestHandler):
    def respond(self, **kwargs):
        self.response.out.write(json.dumps(kwargs))

    def get_game(self):
        id = self.request.get("game_uid")
        if not id:
            self.error(422)
        gd, game = load_game(id)
        if not game:
            self.error(404)
        boards = [b.dictify() for b in game.boards]
        moves = [ChessMove.dictify(m) for m in game.moves]
        return self.respond(status='ok', boards=boards, moves=moves)

    def do_move(self, data):
        uid = self.request.get("game_uid")
        move = data.get("move")
        turn = data.get("turn")
        if None in [uid, move, turn]:
            self.error(422)
        gd, game = load_game(uid)
        if game is None:
            self.error(404)
        turn = int(turn)
        ui = AsciiUI(game)
        ok = ui.goto_turn(turn)
        if ok:
            if move == 'undo':
                gd.delete()
            else:
                ok = ui.do_command(move)
                if ok:
                    make_gd(uid, ui.game).put()
        return self.respond(status='ok', msg=ui.last_msg, success=ok)

    def get(self):
        action = self.request.get("action")
        if action == "get_game":
            return self.get_game()
        self.error(404)

    def post(self):
        data = json.loads(self.request.body)
        action = data.get('action')
        logging.error(data)
        if action == "do_move":
            return self.do_move(data)
        self.error(404)

app = webapp.WSGIApplication([
    ('/timechess/games', ChessHandler),
    ('/timechess/new_gui', ChessHandler),
    ('/timechess/new', NewGameHandler),
    ('/timechess/api', JSONChessHandler),
    ('/timechess/game', NewChessHandler),
])
