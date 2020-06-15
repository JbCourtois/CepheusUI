from collections import namedtuple
from random import shuffle

from termcolor import colored


class IndexableMixin:
    _auto_id = 0

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj.__index = IndexableMixin._auto_id
        IndexableMixin._auto_id += 1

        return obj

    def __lt__(self, other):
        return self.__index < other.__index

    def __gt__(self, other):
        return self.__index > other.__index


class Rank(IndexableMixin, str):
    pass


RANKS = [Rank(rank) for rank in [
    'A', 'K', 'Q', 'J', 'T',
    '9', '8', '7', '6', '5', '4', '3', '2',
]]


class Suit(IndexableMixin, namedtuple('Suit', ['letter', 'symbol', 'color'])):
    def __str__(self):
        return self.symbol


SUITS = [
    Suit('s', '♠', 'white'),
    Suit('h', '♥', 'red'),
    Suit('d', '♦', 'yellow'),
    Suit('c', '♣', 'green'),
]


class Card(namedtuple('Card', ['rank', 'suit'])):
    def __str__(self):
        text = ''.join(map(str, [self.rank, self.suit]))
        return colored(text, self.suit.color, attrs=['bold'])

    def to_cepheus(self):
        return ''.join(map(str, [self.rank, self.suit.letter]))


class CardSet(list):
    def __str__(self):
        return ' '.join(map(str, self))

    def to_cepheus(self):
        return ''.join(map(Card.to_cepheus, self))

    def bulkpop(self, nb_cards):
        return self.__class__(self.pop() for _ in range(nb_cards))


def generate_deck():
    deck = CardSet(Card(rank, suit) for rank in RANKS for suit in SUITS)
    shuffle(deck)
    return deck
