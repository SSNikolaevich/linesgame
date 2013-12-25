import random
from .player import Player


def filterCoords(func, board):
    size = board.size()
    coords = []
    for x in xrange(size):
        for y in xrange(size):
            if func(board, x, y):
                coords.append((x, y))
    return coords


def isSource(board, x, y):
    if board.get(x, y) is None:
        return False
    for dx, dy in (-1, 0), (1, 0), (0, -1), (0, 1):
        _x = x + dx
        _y = y + dy
        if board.valid(_x, _y) and (board.get(_x, _y) is None):
            return True
    return False


def isTarget(board, sx, sy, tx, ty):
    return (board.get(tx, ty) is None) and board.feasible(sx, sy, tx, ty)


def getSources(board):
    return filterCoords(isSource, board)


def getTargets(board, sx, sy):
    f = lambda b, x, y: isTarget(b, sx, sy, x, y)
    return filterCoords(f, board)


class RandomBot(Player):
    def __init__(self):
        super(RandomBot, self).__init__()

    def getMove(self, game):
        board = game.board()
        sx, sy = random.choice(getSources(board))
        tx, ty = random.choice(getTargets(board, sx, sy))
        return sx, sy, tx, ty

