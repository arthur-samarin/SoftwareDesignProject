import collections
import sys, json
Card = collections.namedtuple('Card', ['rank', 'suit'])

class Player:
    _cards = {'spades': [], 'diamonds': [], 'clubs': [], 'hearts': []}

    def __init__(self, id):
        self._id = id

    def insert_cards(self, cards):
        for (rank, suit) in cards:
            self._cards[suit].append(rank)

    def start(self):
        while True:
            data = json.loads(sys.stdin.readline())
            gameData = data['gameData']
            if data['state'] == 'end':
                return

            if data['state'] == 'init':
                self.power_rank = gameData['powerRanks']
                self._trump = gameData['trump']

            cardsOnTable = []

            if gameData is not None:
                newCardId = 'newCards' + self._id
                if newCardId in gameData:
                    newCards = gameData[newCardId]
                    self.insert_cards(newCards)

            if data['state'] == 'wait' or data['state'] == 'init':
                continue

            if gameData is not None and 'cardsOnTable' in gameData:
                cardsOnTable = gameData["cardsOnTable"]

            result = {}
            result["cardsOnTable"] = cardsOnTable

            if len(cardsOnTable) % 2 == 0:
                result["putCards"] = self.attack()
            else:
                (a, b) = cardsOnTable[-1]
                result["putCards"] = self.protection(Card(a, b))

            print(json.dumps(result))

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


if __name__ == "__main__":
    Player(sys.argv[1]).start()
