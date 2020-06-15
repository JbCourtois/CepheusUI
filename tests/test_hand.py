from random import seed

from unittest import TestCase
from unittest.mock import patch

from cepheus.hand import Hand


@patch('cepheus.hand.LoggerMixin.log')
class TestHand(TestCase):
    def setUp(self):
        seed(42)
        self.hand = Hand()

    def test_hand(self, mock_log):
        # Preflop
        self.hand.apply_raise()
        self.hand.apply_raise()
        self.hand.apply_call()

        # Flop
        self.hand.apply_call()
        self.hand.apply_call()

        # Turn
        self.hand.apply_raise()
        self.hand.apply_raise()

        self.assertEqual(self.hand.get_state(), 'rrc/cc/rr:ThJcJdQs')
