import sys
import json
import subprocess
from twisted.internet import protocol, reactor, endpoints, defer
from twisted.protocols import basic
from Card import Card
from random import choice, shuffle
import time

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

    def remove(self, card):
        assert (card in self._cards), 'No such element to delete'
        self._cards.remove(card)


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
        for i in range(n):
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
        pass

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
        print("********")
        print(rData)
        print("********")
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
    def __init__(self):
        global port
        self.clients = {}
        self.game = CardGame()
        with open('runner.config') as f:
            data = json.load(f)

        for i in range(2):
            strategyPath = data[f'player_{i}']
            strategyId = data[f'player_{i}_Id']
            subprocess.Popen(["python", strategyPath, f'{strategyId}', f'{port}'])
            print("run child")

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

            reactor.callLater(2, continuation)

            self.curState += 1
            return

        if self.curState >= 2:
            if (not self.OnVaidate(id, data)):
                # Do logic for invalid move
                return

            # result in None if game is ended
            result = self.OnPlayerMove(id, data)
            if result is None:
                result = self.OnCheckWin()
                answer["state"] = "end"
                answer["gameData"] = result
                self.clients[0].transport.write(json.dumps(answer).encode())
                self.clients[0].transport.doWrite()

                self.clients[1].transport.write(json.dumps(answer).encode())
                self.clients[1].transport.doWrite()

                # TODO close server
                return

            answer["state"] = "wait"
            answer["gameData"] = result
            self.clients[id].transport.write(json.dumps(answer).encode())
            self.clients[id].transport.doWrite()

            answer["state"] = "move"
            self.clients[1 - id].transport.write(json.dumps(answer).encode())
            self.clients[1 - id].transport.doWrite()

            pass

    def OnPlayerConnected(self, id):
        data = self.game.GetInitialDataForPlayer(id)
        return data

    def OnVaidate(self, id, data):
        return self.game.Validate(id, data);

    def OnPlayerMove(self, id, data):
        return self.game.HandlePlayerMove(id, data)

    def OnCheckWin(self):
        return self.game.CheckWin()



if __name__ == '__main__':
    reactor.listenTCP(port, Runner())
    reactor.run()




    #
    # print(sys.argv)
    # game = Game(1, 2)
    # f = open('log.txt', 'w')
    # res = game.run(f)
    # print(res)