import os
import random
import logging


class Board:
    def __init__(self, size):
        self.__data = [[None] * size for i in xrange(size)]

    def valid(self, x, y):
        size = self.size()
        return (x >= 0) and (x < size) and (y >= 0) and (y < size)

    def size(self):
        return len(self.__data)

    def __checkCoords(self, x, y):
        if not self.valid(x, y):
            raise Exception("Wrong coordinates.")

    def get(self, x, y):
        self.__checkCoords(x, y)
        return self.__data[x][y]

    def set(self, x, y, value):
        self.__checkCoords(x, y)
        self.__data[x][y] = value

    def swap(self, x1, y1, x2, y2):
        self.__checkCoords(x1, y1)
        self.__checkCoords(x2, y2)
        v = self.__data[x1][y1]
        self.__data[x1][y1] = self.__data[x2][y2]
        self.__data[x2][y2] = v


def feasible(board, x1, y1, x2, y2):
    opened = {(x1, y1): 0}
    closed = set()
    maxCost = board.size() ** 2
    while opened and ((x2, y2) not in closed):
        items = opened.items()
        items.sort(key=lambda i: i[1])
        coords, cost = items[0]
        closed.add(coords)
        x, y = coords
        opened.pop(coords)
        for dx in xrange(-1, 2):
            for dy in xrange(-1, 2):
                if dx or dy:
                    _x = x + dx
                    _y = y + dy
                    if (
                        board.valid(_x, _y)
                        and (board.get(_x, _y) is None)
                        and ((_x, _y) not in closed)
                        and (opened.get((_x, _y), maxCost) > cost)
                    ):
                        opened[(_x, _y)] = cost + 1
    return (x2, y2) in closed


class ReadonlyBoardView:
    def __init__(self, board):
        self.__board = board

    def valid(self, x, y):
        return self.__board.valid(x, y)

    def size(self):
        return self.__board.size()

    def get(self, x, y):
        return self.__board.get(x, y)


class ReadOnlyGameView:
    def __init__(self, game):
        self.__game = game

    def lineSize(self):
        return self.__game.lineSize()

    def board(self):
        return self.__game.board()

    def next(self):
        return self.__game.next()

    def isOver(self):
        return self.__game.isOver()

    def __str__(self):
        return str(self.__game)


class Game:
    COLORS = ["red", "green", "blue", "yellow", "magenta", "cyan", "brown"]

    def __init__(self, size=9, lineSize=5, appendCount=3, seed=None):
        if size < lineSize:
            msg = "Wrong combination of size and line size " \
                  "(size: %d, line size: %d)" % (size, lineSize)
            raise Exception(msg)
        self.__logger = logging.getLogger("game")
        self.__logger.debug(
            "Start new game. Board size: %d, "
            "line size: %d, append stones: %d, "
            "seed: %s.",
            size,
            lineSize,
            appendCount,
            repr(seed)
        )
        self.__board = Board(size)
        self.__lineSize = lineSize
        self.__appendCount = appendCount
        self.__isOver = False
        self.__score = 0
        self.__bonusScore = 0
        random.seed(seed)
        self.__createNext()
        self.__update()

    def __getStonesInLine(self, x, y, dx, dy, color):
        stones = []
        if self.__board.get(x, y) == color:
            stones.append((x, y))
            x1 = x + dx
            y1 = y + dy
            if self.__board.valid(x1, y1):
                stones += self.__getStonesInLine(x1, y1, dx, dy, color)
        return stones

    def __removeStones(self):
        size = self.__board.size()
        deltas = (-1, 1), (0, 1), (1, 1), (1, 0)
        removedStones = set()
        for x in xrange(size):
            for y in xrange(size):
                color = self.__board.get(x, y)
                if color is not None:
                    for dx, dy in deltas:
                        stones = self.__getStonesInLine(x, y, dx, dy, color)
                        if len(stones) >= self.__lineSize:
                            removedStones.update(stones)
        for x, y in removedStones:
            self.__logger.debug("Remove stone in (%d, %d).", x, y)
            self.__board.set(x, y, None)
        return removedStones

    def __insertStones(self):
        coords = []
        size = self.__board.size()
        for x in xrange(size):
            for y in xrange(size):
                if self.__board.get(x, y) is None:
                    coords.append((x, y))
        self.__isOver = len(coords) <= self.__appendCount
        random.shuffle(coords)
        for color, coords in zip(self.__next, coords):
            x, y = coords
            self.__logger.debug(
                "Insert %s stone into (%d, %d).",
                color,
                x,
                y
            )
            self.__board.set(x, y, color)

    def __createNext(self):
        self.__next = tuple(
            random.choice(Game.COLORS)
                for i in xrange(self.__appendCount)
        )
        self.__logger.debug("Next stones: %s.", ", ".join(self.__next))

    def __stonesCost(self, stones):
        stonesCount = len(stones)
        if stonesCount:
            return 2 * (stonesCount ** 2) - 20 * stonesCount + 60 \
                + self.__bonusScore
        else:
            return 0

    def __updateScore(self, removedStones):
        self.__score += self.__stonesCost(removedStones)

    def __update(self):
        removedStones = self.__removeStones()
        self.__updateScore(removedStones)
        self.__insertStones()
        self.__createNext()

    def lineSize(self):
        return self.__lineSize

    def board(self):
        return ReadonlyBoardView(self.__board)

    def next(self):
        return self.__next

    def isOver(self):
        return self.__isOver

    def readOnlyView(self):
        return ReadOnlyGameView(self)

    def makeMove(self, x1, y1, x2, y2):
        self.__logger.debug("Move (%d, %d) -> (%d, %d).", x1, y1, x2, y2)
        if self.__isOver:
            raise Exception("Game is over")
        if (x1 == x2) and (y1 == y2):
            raise Exception("Wrong coordinates.")
        if self.__board.get(x1, y1) is None:
            raise Exception("Start position is empty")
        if self.__board.get(x2, y2) is not None:
            raise Exception("End position is not empty")
        if feasible(self.__board, x1, y1, x2, y2):
            self.__board.swap(x1, y1, x2, y2)
        self.__update()
        self.__logger.debug("Score: %d", self.__score)

    def score(self):
        return self.__score

    def __str__(self):
        l = []
        size = self.__board.size()
        for y in xrange(size):
            s = ""
            for x in xrange(size):
                v = self.__board.get(x, y)
                if v is None:
                    s += "."
                else:
                    s += v[0]
            l.append(s)
        l.append("Next  : %s" % ("".join(map(lambda i: i[0], self.__next))))
        l.append("Score : %d" % (self.__score))
        if self.__isOver:
            l.append("Game is over")
        l.append("")
        return os.linesep.join(l)
