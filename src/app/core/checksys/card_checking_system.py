import sys
import json
import subprocess
from twisted.internet import protocol, reactor, endpoints, defer
from twisted.protocols import basic
from Card import Card
from random import choice, shuffle
import time

from app.core.checksys import CheckingSystem, GameVerdict
from app.model import SourceCode

port = 10001

class Game:
    def GetInitialDataForPlayer(self, id):
        pass

    def Validate(self, id, data):
        pass

    def HandlePlayerMove(self, id, data):
        pass

    def CheckWin(self):
        pass


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()
    power_rank = {key: value for (value, key) in enumerate(ranks)}

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                       for rank in self.ranks]
        shuffle(self._cards)

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, pos):
        return self._cards[pos]

    def get_and_del(self, pos):
        item = self._cards[pos]
        del self._cards[pos]
        return item


# noinspection PyDictCreation
class CardGame(Game):

    def __init__(self):
        self._deck = FrenchDeck()
        self._trump = choice(self._deck.suits)
        self._attackPlayer = 0
        self._protectPlayer = 1
        self.cardOnTable = []
        self.playersCardCount = {0 : 6, 1 : 6}

    def get_cards(self, n):
        cards = []
        size = len(self._deck)
        for i in range(min(n, size)):
            cards.append(self._deck.get_and_del(-1))
        return cards

    def GetInitialDataForPlayer(self, id):
        result = {"trump" : self._trump, "cardsOnTable": None, "putCards": None,
                  "powerRanks" : self._deck.power_rank}
        result[f'newCards{id}'] = self.get_cards(6)
        return result

    def Validate(self, id, data):
        return True


    def HandlePlayerMove(self, id, data):
        result = {}
        # check that id is right
        if len(self._deck) == 0 and \
                (self.playersCardCount[0] == 0 or self.playersCardCount[1] == 0):
            return result
        result["cardsInDeck"] = len(self._deck)
        result["id"] = id
        if ("putCards" in data):
            card = data["putCards"]
        else:
            card = None

        if self._attackPlayer == id:
            if card is None:
                result["cardsOnTable"] = []
                self._attackPlayer = 1 - self._attackPlayer
                self._protectPlayer = 1 - self._attackPlayer

                newCards = self.get_cards(6 - self.playersCardCount[1 - id])
                result[f'newCards{1 - id}'] = newCards
                self.playersCardCount[1 - id] += len(newCards)

                newCards = self.get_cards(6 - self.playersCardCount[id])
                result[f'newCards{id}'] = newCards
                self.playersCardCount[id] += len(newCards)
            else:
                result["cardsOnTable"] = data["cardsOnTable"] + [card]
                self.playersCardCount[id] -= 1
        else:
            if card is None:
                result[f'newCards{id}'] = data["cardsOnTable"]
                self.playersCardCount[id] += len(data["cardsOnTable"])

                newCards = self.get_cards(6 - self.playersCardCount[1 - id])
                result[f'newCards{1 - id}'] = newCards
                self.playersCardCount[1 - id] += len(newCards)
                result["cardsOnTable"] = []
            else:
                result["cardsOnTable"] = data["cardsOnTable"] + [card]
                self.playersCardCount[id] -= 1

        return result

    def CheckWin(self):
        if len(self._deck) == 0:
            if self.playersCardCount[1] == 0 and self.playersCardCount[0] == 0:
                return -1
            for i in range(2):
                if self.playersCardCount[i] == 0:
                    return i

    @staticmethod
    def write_list_cards(l, f):
        for item in l:
            f.write('(' + item.rank + ' ' + item.suit + '), ')
        f.write('\n')

    def compare(self, card1, card2):
        if card1.suit != card2.suit:
            if card1.suit == self._trump:
                return 1
            elif card2.suit == self._trump:
                return -1
            else:
                raise Exception('invalid card')
        else:
            return -1 if self._deck.power_rank[card1.rank] < self._deck.power_rank[card2.rank] \
                else 1


class StrategyProtocol(basic.LineReceiver):

    def connectionMade(self):
        self.transport.setTcpNoDelay(True)

    def dataReceived(self, rData):
        data = json.loads(rData)
        id = data["id"]
        clients = self.factory.clients
        if id not in clients:
            clients[id] = self
            self.factory.OnDataRecieved(id)
        else:
            self.factory.OnDataRecieved(id, data)


class Runner(protocol.ServerFactory):
    protocol = StrategyProtocol
    curState = 0

    def __init__(self, id1, src1 : SourceCode, id2, src2 : SourceCode):
        global port

        self.mapping = {0 : id1, 1 : id2}
        with open(src1.filename, 'w') as f:
            f.write(src1.code)

        with open(src2.filename, 'w') as f:
            f.write(src2.code)

        self.clients = {}
        self.game = CardGame()
        with open('runner.config') as f:
            data = json.load(f)

        self.runStrategy(src1.filename, 0, port)
        self.runStrategy(src2.filename, 1, port)

    def runStrategy(self, path, id, port):
        subprocess.Popen(["python", path, f'{id}', f'{port}'])

    def OnDataRecieved(self, id, data = None):
        answer = {}
        if self.curState == 0:
            answer["state"] = "init"
            answer["gameData"] = self.OnPlayerConnected(id)
            print(json.dumps(answer))
            self.clients[id].transport.write(json.dumps(answer).encode())
            self.clients[id].transport.doWrite()

            print(f'{id} has connected')
            self.curState += 1
            return

        if self.curState == 1:
            print(f'{id} has connected')
            print('Game started')
            answer["state"] = "init"
            answer["gameData"] = self.OnPlayerConnected(id)
            print(json.dumps(answer))
            self.clients[id].transport.write(json.dumps(answer).encode())
            #https: // stackoverflow.com / questions / 3617584 / twisted - transport - write

            def continuation():
                self.clients[id].transport.doWrite()
                answer["state"] = "move"
                answer["gameData"] = {"cardsOnTable" : []}
                self.clients[0].transport.write(json.dumps(answer).encode())
                self.clients[0].transport.doWrite()

            reactor.callLater(0.1, continuation)

            self.curState += 1
            return

        if self.curState >= 2:
            if not self.OnVaidate(id, data):
                # Do logic for invalid move
                return

            # result in None if game is ended
            result = self.OnPlayerMove(id, data)
            if result == {}:
                result = self.OnCheckWin()
                answer["state"] = "end"
                answer["gameData"] = str(result)
                self.clients[0].transport.write(json.dumps(answer).encode())
                self.clients[0].transport.doWrite()

                self.clients[1].transport.write(json.dumps(answer).encode())
                self.clients[1].transport.doWrite()

                reactor.stop()
                return

            answer["state"] = "wait"
            answer["gameData"] = result
            self.clients[id].transport.write(json.dumps(answer).encode())
            self.clients[id].transport.doWrite()

            def continuation():
                answer["state"] = "move"
                self.clients[1 - id].transport.write(json.dumps(answer).encode())
                self.clients[1 - id].transport.doWrite()

            reactor.callLater(0.1, continuation)
            pass

    def OnPlayerConnected(self, id):
        data = self.game.GetInitialDataForPlayer(id)
        return data

    def OnVaidate(self, id, data):
        return self.game.Validate(id, data)

    def OnPlayerMove(self, id, data):
        return self.game.HandlePlayerMove(id, data)
`
    def OnCheckWin(self):
        return self.game.CheckWin()


result = None
class check(CheckingSystem):
    def evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        global result
        reactor.listenTCP(port, Runner(id1, source1, id2, source2))
        reactor.run()
        return result
