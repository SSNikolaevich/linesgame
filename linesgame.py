import os
import random

class Game:
    COLORS = [
        "red", "green", "white", "yellow",
        "magenta", "blue", "cyan", "brown"
    ]

    def __init__(self, size, lineSize, appendCount=3, seed=None):
        if size < lineSize:
            msg = "Wrong combination of size and line size " \
                  "(size: %d, line size: %d)" % (size, lineSize)
            raise Exception(msg)
        self.__size = size
        self.__lineSize = lineSize
        self.__appendCount = appendCount
        self.__layout = [[None] * size for i in xrange(size)]
        self.__isGameOver = False
        self.__score = 0
        random.seed(seed)
        self.__createNext()
        self.__update()

    def __createNext(self):
        self.__next = [
            random.choice(Game.COLORS)
                for i in xrange(self.__appendCount)
        ]

    def __update(self):
        coords = []
        for x in xrange(self.__size):
            for y in xrange(self.__size):
                if self.__layout[x][y] is None:
                    coords.append((x, y))
        self.__isGameOver = len(coords) <= self.__appendCount
        random.shuffle(coords)
        for color, coords in zip(self.__next, coords):
            x, y = coords
            self.__layout[x][y] = color
        self.__createNext()

    def next(self):
        return self.__next

    def isGameOver(self):
        return self.__isGameOver

    def move(self, x1, y1, x2, y2):
        if self.__isGameOver:
            raise Exception("Game is over")
        if (
            (x1 < 0)
            or (x1 >= self.__size)
            or (y1 < 0)
            or (y1 >= self.__size)
            or (x2 < 0)
            or (x2 >= self.__size)
            or (y2 < 0)
            or (y2 >= self.__size)
            or ((x1 == x2) and (y1 == y2))
        ):
            raise Exception("Wrong coordinates.")
        if self.__layout[x1][y1] is None:
            raise Exception("Start position is empty")
        if self.__layout[x2][y2] is not None:
            raise Exception("End position is not empty")
        if self.feasable(x1, y1, x2, y2):
            self.__layout[x2][y2] = self.__layout[x1][y1]
            self.__layout[x1][y1] = None
        self.__update()

    def score(self):
        return self.__score

    def __repr__(self):
        l = []
        for y in xrange(self.__size):
            s = ""
            for x in xrange(self.__size):
                v = self.__layout[x][y]
                if v is None:
                    s += "."
                else:
                    s += v[0]
            l.append(s)
        l.append("Next: %s" % ("".join(map(lambda i: i[0], self.__next))))
        if self.__isGameOver:
            l.append("Game is over")
        l.append("")
        return os.linesep.join(l)

    def feasable(self, x1, y1, x2, y2):
        current = [(x1, y1)]
        l = [[False] * self.__size for x in xrange(self.__size)]
        l[x1][y1] = True
        while True:
            i = 0
            for x in xrange(self.__size):
                for y in xrange(self.__size):
                    if (
                        (self.__layout[x][y] is None)
                        and (not l[x][y])
                        and (
                            (x and l[x - 1][y])
                            or (y and l[x][y - 1])
                            or ((x < self.__size - 1) and l[x + 1][y])
                            or ((y < self.__size - 1) and l[x][y + 1])
                        )
                    ):
                        l[x][y] = True
                        i += 1
            if not i:
                break
        return l[x2][y2]

