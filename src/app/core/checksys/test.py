import collections
import sys, json
Card = collections.namedtuple('Card', ['rank', 'suit'])
port = 0
id = 0


class Player(Protocol):
    _cards = {'spades': [], 'diamonds': [], 'clubs': [], 'hearts': []}

    def connectionMade(self):
        global id
        self.transport.write(('{ "id" : ' + str(id) + '}').encode())

    def insert_cards(self, cards):
        for (rank, suit) in cards:
            self._cards[suit].append(rank)

    def dataReceived(self, rData):
        global id
        print("-----")

        print(rData)
        print("------")

        data = json.loads(rData)
        gameData = data['gameData']

        if data['state'] == 'end':
            return
        if data['state'] == 'init':
            self.power_rank = gameData['powerRanks']
            self._trump = gameData['trump']

        newCardId = 'newCards' + str(id)
        if newCardId in gameData:
            newCards = gameData[newCardId]
            self.insert_cards(newCards)

        if data['state'] == 'wait' or data['state'] == 'init':
            return

        cardsOnTable = gameData["cardsOnTable"]

        result = {}
        result["cardsOnTable"] = cardsOnTable

        if len(cardsOnTable) % 2 == 0:
            result["putCards"] = self.attack()
        else:
            (a, b) = cardsOnTable[-1]
            result["putCards"] = self.protection(Card(a, b))

        result["id"] = id
        self.transport.write(json.dumps(result).encode())

    def get_min_rank(self, ranks):
        min_rank = ranks[0]
        for rank in ranks[1:]:
            if self.power_rank[min_rank] > self.power_rank[rank]:
                min_rank = rank
        return min_rank

    def attack(self):
        min_card = Card(None, None)
        for suit in self._cards.keys():
                if len(self._cards[suit]) > 0:
                    rank = self.get_min_rank(self._cards[suit])
                    if min_card == Card(None, None) or min_card.suit == self._trump:
                        min_card = Card(rank, suit)
                    elif suit != self._trump:
                        if self.power_rank[min_card.rank] > self.power_rank[rank]:
                            min_card = Card(rank, suit)
        if min_card != Card(None, None):
            self._cards[min_card.suit].remove(min_card.rank)

        if min_card == Card(None, None):
            return None
        return min_card

    def protection(self, card):
        suitable_card = Card(None, None)
        ranks = list(self._cards[card.suit])
        for rank in ranks:
            if self.power_rank[card.rank] < self.power_rank[rank]:
                if suitable_card == Card(None, None) or \
                        self.power_rank[suitable_card.rank] > self.power_rank[rank]:
                    suitable_card = Card(rank, card.suit)
        if suitable_card == Card(None, None) and card.suit != self._trump:
            if len(self._cards[self._trump]) > 0:
                rank = self.get_min_rank(self._cards[self._trump])
                suitable_card = Card(rank, self._trump)
        if suitable_card != Card(None, None):
            self._cards[suitable_card.suit].remove(suitable_card.rank)

        if suitable_card == Card(None, None):
            return None
        return suitable_card


class EchoClientFactory(ClientFactory):
    def buildProtocol(self, addr):
        return Player()


if __name__ == "__main__":
    id = int(sys.argv[1])
    port = int(sys.argv[2])

    with open('log-id' + str(id), 'w') as f:
        f.write("hi")
