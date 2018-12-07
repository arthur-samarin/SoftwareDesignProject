import collections
from random import choice

from app.core import Game

Card = collections.namedtuple('Card', ['rank', 'suit'])

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


class CardGame(Game):
    def __init__(self):
        super.__init__("Card", "Card")
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

    def get_initial_data_for_player(self, id):
        result = {"trump" : self._trump, "cardsOnTable": None, "putCards": None,
                  "powerRanks" : self._deck.power_rank}
        result[f'newCards{id}'] = self.get_cards(6)
        return result

    def validate_move(self, id, data):
        return True


    def handle_player_move(self, id, data):
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

    def check_win(self):
        result = {}

        if len(self._deck) == 0:
            if self.playersCardCount[1] == 0 and self.playersCardCount[0] == 0:
                result['win_id'] = -1
            for i in range(2):
                if self.playersCardCount[i] == 0:
                    result['win_id'] = i
        return result

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
