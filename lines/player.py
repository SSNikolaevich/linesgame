import abc


class Player(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getMove(self, game):
        raise NotImplementedError()


def play(game, player):
    while not game.isOver():
        move = player.getMove(game.readOnlyView())
        game.makeMove(*move)
    return game.score()
