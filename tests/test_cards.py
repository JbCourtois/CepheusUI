from unittest import TestCase
from unittest.mock import patch

from cepheus.cards import generate_deck


def mock_color(text, *args, **kwargs):
    return text


@patch('cepheus.cards.colored', mock_color)
class TestDeck(TestCase):
    def test_deck(self):
        deck = generate_deck()
        deck.sort()

        deuces = deck.bulkpop(4)
        self.assertEqual(str(deuces), '2♣ 2♦ 2♥ 2♠')
        self.assertEqual(deuces.to_cepheus(), '2c2d2h2s')
