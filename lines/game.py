import os
import random


class Board:
    def __init__(self, size):
        self.__data = [[None] * size for i in xrange(size)]

    def valid(self, x, y):
        size = self.size()
        return (x >= 0) and (x < size) and (y >= 0) and (y < size)

    def size(self):
        return len(self.__data)

    def checkCoords(self, x, y):
        if not self.valid(x, y):
            raise Exception("Wrong coordinates.")

    def get(self, x, y):
        self.checkCoords(x, y)
        return self.__data[x][y]

    def set(self, x, y, value):
        self.checkCoords(x, y)
        self.__data[x][y] = value

    def swap(self, x1, y1, x2, y2):
        self.checkCoords(x1, y1)
        self.checkCoords(x2, y2)
        v = self.__data[x1][y1]
        self.__data[x1][y1] = self.__data[x2][y2]
        self.__data[x2][y2] = v

    def feasable(self, x1, y1, x2, y2):
        opened = {(x1, y1): 0}
        closed = set()
        maxCost = self.size() ** 2
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
                            self.valid(_x, _y)
                            and (self.__data[_x][_y] is None)
                            and ((_x, _y) not in closed)
                            and (opened.get((_x, _y), maxCost) > cost)
                        ):
                            opened[(_x, _y)] = cost + 1
        return (x2, y2) in closed


class Game:
    COLORS = ["red", "green", "blue", "yellow", "magenta", "cyan", "brown"]

    def __init__(self, size=9, lineSize=5, appendCount=3, seed=None):
        if size < lineSize:
            msg = "Wrong combination of size and line size " \
                  "(size: %d, line size: %d)" % (size, lineSize)
            raise Exception(msg)
        self.__board = Board(size)
        self.__lineSize = lineSize
        self.__appendCount = appendCount
        self.__isGameOver = False
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
            self.__board.set(x, y, None)
        return removedStones

    def __insertStones(self):
        coords = []
        size = self.__board.size()
        for x in xrange(size):
            for y in xrange(size):
                if self.__board.get(x, y) is None:
                    coords.append((x, y))
        self.__isGameOver = len(coords) <= self.__appendCount
        random.shuffle(coords)
        for color, coords in zip(self.__next, coords):
            x, y = coords
            self.__board.set(x, y, color)

    def __createNext(self):
        self.__next = [
            random.choice(Game.COLORS)
                for i in xrange(self.__appendCount)
        ]

    def __stonesCost(self, stones):
        stonesCount = len(stones)
        return 2 * (stonesCount ** 2) - 20 * stonesCount + 60 \
            + self.__bonusScore

    def __updateScore(self, removedStones):
        self.__score += self.__stonesCost(removedStones)

    def __update(self):
        removedStones = self.__removeStones()
        self.__updateScore(removedStones)
        self.__insertStones()
        self.__createNext()

    def next(self):
        return self.__next

    def isGameOver(self):
        return self.__isGameOver

    def makeMove(self, x1, y1, x2, y2):
        if self.__isGameOver:
            raise Exception("Game is over")
        if (x1 == x2) and (y1 == y2):
            raise Exception("Wrong coordinates.")
        if self.__board.get(x1, y1) is None:
            raise Exception("Start position is empty")
        if self.__board.get(x2, y2) is not None:
            raise Exception("End position is not empty")
        if self.__board.feasable(x1, y1, x2, y2):
            self.__board.swap(x1, y1, x2, y2)
        self.__update()

    def score(self):
        return self.__score

    def __repr__(self):
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
        if self.__isGameOver:
            l.append("Game is over")
        l.append("")
        return os.linesep.join(l)
