function coord2alg(x,y) {
  return 'abcdefghijklmnopqrstuvwxyz'[x]+(y+1).toString();
}

function renderPiece(piece) {
  if (piece === null) return '';
  return 'WB'[piece.player] + piece.short;
}


angular.module("chess", [], function($locationProvider) {
      $locationProvider.html5Mode(true);
    })
  .directive("ngBindAttr", function($interpolate) {
    return function(scope, element, attr) {
      var lastValue = {};
      var interpolateFns = {};
      scope.$watch(function() {
        var values = scope.$eval(attr.ngBindAttr);
        for(var key in values) {
          var exp = values[key],
          fn = (interpolateFns[exp] ||
            (interpolateFns[values[key]] = $interpolate(exp))),
          value = fn(scope);
          if (lastValue[key] !== value) {
            attr.$set(key, lastValue[key] = value);
          }
        }
      });
    };
  });


function ChessGameCtrl($scope, $http, $location) {
  $scope.uid = ($location.search()).game_uid;
  $scope.turn = 0;
  $scope.board = null;
  $scope.renderPiece = renderPiece;
  $scope.url = '/timechess/api?game_uid='+$scope.uid;
  $scope.target = null;
  $scope.cell_size = 60;
  $scope.message = "No Message.";
  $scope.game_loaded = false;
  window.foo = $scope;
  window.bar = $location;

  $scope.set_data = function(data, turn) {
    $scope.gamedata = data;
    // Precompute board size
    $scope.num_turns = data.boards.length;
    var rebuild_board = false
    var w = data.boards[0].cells.length;
    var h = data.boards[0].cells[0].length;
    if ($scope.board === null || w !== $scope.board_width || h != $scope.board_height) {
      $scope.board = [];
      for (var j = 0; j < h; j++) {
        $scope.board[j] = [];
        for (var i = 0; i < w; i++) {
          $scope.board[j][i] = {
            piece: null,
            alg: coord2alg(i,h-j-1),
            x: i,
            y: j
          };
        }
      }
      $scope.board_width = w;
      $scope.board_height = h;
    }
    // Label the moves
    $scope.moves = data.moves;
    for (var mnum = 0; mnum < $scope.moves.length; mnum++) {
      var m = $scope.moves[mnum];
      m.num = mnum;
      m.start_alg = coord2alg(m.start[0], m.start[1]);
      m.end_alg = coord2alg(m.end[0], m.end[1]);
    }
    // Set turn if requested
    if (turn === undefined)
      turn = $scope.num_turns;
    $scope.goto_turn(turn);
    $scope.game_loaded = true;
  };

  $scope.reload = function(turn) {
    $http.get($scope.url+"&action=get_game")
      .success(function(data) {
        $scope.set_data(data, turn);
      });
  };

  $scope.domove = function(move) {
    var turn = $scope.turn;
    $http.post($scope.url, {action:"do_move", turn:turn, move:move})
    .success(function(data) {
      if (data.success) {
        $scope.reload($scope.turn+1);
      }
      $scope.message = data.msg;
    });
  };

  $scope.select = function(cell) {
    if ($scope.target) {
      if ($scope.target.alg != cell.alg) {
        var move = $scope.target.alg + "-" + cell.alg;
        $scope.domove(move)
      }
      $scope.target = null;
    } else {
      $scope.target = cell;
    }
  };

  $scope.goto_turn = function(turn) {
    if (turn < 0)
      turn = 0;
    if (turn >= $scope.num_turns)
      turn = $scope.num_turns-1;
    // XXX Scroll Stuff goes here
    // SEE http://stackoverflow.com/questions/12790854/angular-directive-to-scroll-to-a-given-item
    // And also http://stackoverflow.com/questions/344615/scroll-position-of-div-with-overflow-auto
    // Want to grab the scroll box and let it scroll to a position!
    // Problem: the below runs before the GUI updates, so it's using the
    // previous tr.curr
    // Also it doesn't run at the start.
    var mw = $(".movewrapper");
    var movetrs = $(".moves tr");
    if (mw.length && (movetrs.length > turn)) {
      mw[0].scrollTop = movetrs[turn].offsetTop-220;
    }
    if ($scope.game_loaded && turn == $scope.turn)
      return;
    $scope.target = null;
    $scope.turn = turn;
    // Store current move for ease of lookup
    $scope.m = $scope.moves[turn];
    var w = $scope.board_width;
    var h = $scope.board_height;
    var b = $scope.gamedata.boards[turn].cells;
    for (var j = 0; j < h; j++) {
      for (var i = 0; i < w; i++) {
        var cell = $scope.board[j][i];
        var cp = cell.piece;
        var piece = b[i][h-j-1];
        if (cp === piece)
          continue;
        var update = false;
        if (cp === null || piece === null)
          update = true;
        else if (cp.player !== piece.player || cp.name !== piece.name)
          update = true;
        if (update) {
          cell.piece = piece;
        }
      }
    }
  };

  $scope.next = function() {
    $scope.goto_turn($scope.turn+1);
  };

  $scope.prev = function() {
    $scope.goto_turn($scope.turn-1);
  };

  $scope.reload();

  $(document).keydown(function(e){
    if ($("input:focus").length) {
      return true;
    };
    if (e.keyCode == 37 || e.keyCode == 38) {
      $scope.prev();
      $scope.$apply();
      return false;
    } else if (e.keyCode == 39 || e.keyCode == 40) {
      $scope.next();
      $scope.$apply();
      return false;
    }
  });
}