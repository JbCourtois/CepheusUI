from io import StringIO
from enum import Enum

from cepheus.cards import generate_deck, CardSet


class LoggerMixin:
    def __init__(self, *args, logger=None, **kwargs):
        self.logger = logger
        super().__init__(*args, **kwargs)

    def log(self, *args, **kwargs):
        print(*args, **kwargs, file=self.logger)


class Hand(LoggerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pot = 1
        self.round_id = 0
        self.deck = generate_deck()
        self.table_cards = CardSet()

        self.history = StringIO()
        self.active_player = 0
        self.nb_raises = 1
        self.bb_can_check = True

        self.sb_cards = self.deck.bulkpop(2)
        self.bb_cards = self.deck.bulkpop(2)

    def switch_active_player(self):
        self.active_player = 1 - self.active_player

    def next_round(self):
        self.history.write('/')

        for _ in range(1 if self.round_id > 0 else 3):
            self.table_cards.append(self.deck.pop())

        self.log('Pot:', self.pot)
        self.log('Table:', self.table_cards)

        self.round_id += 1
        self.active_player = 0
        self.nb_raises = 0
        self.bb_can_check = True

    def apply_call(self):
        self.history.write('c')
        if self.active_player == 1 or not self.bb_can_check:
            self.next_round()
        else:
            self.switch_active_player()

    def apply_raise(self):
        self.history.write('r')
        self.pot += (2 if self.nb_raises else 1)
        self.bb_can_check = False
        self.nb_raises += 1
        self.switch_active_player()

    def get_state(self):
        return f'{self.history.getvalue()}:{self.table_cards.to_cepheus()}'


class Actions(Enum):
    FOLD = 'F'
    CALL = 'C'
    RAISE = 'R'


ActionLabels = {
    Actions.FOLD: 'folds',
    Actions.CALL: 'calls',
    Actions.RAISE: 'raises',
}


class HandUI(LoggerMixin):
    def __init__(self, sb_client, bb_client, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.hand = Hand(logger=self.logger)
        self.clients = {
            0: sb_client('Small Blind', self.hand.sb_cards),
            1: bb_client('Big Blind', self.hand.bb_cards),
        }

    def play(self):
        while self.hand.round_id < 4:
            action = self.get_action()
            if action == Actions.FOLD:
                self.show_cards()
                break
            elif action == Actions.CALL:
                self.hand.apply_call()
            elif action == Actions.RAISE:
                self.hand.apply_raise()
            else:
                raise ValueError('Bad action:', action)
        else:
            self.showdown()

    def get_action(self):
        action = None
        client = self.clients[self.hand.active_player]
        hand_state = self.hand.get_state()

        while action is None:
            raw_action = client.get_action(hand_state)
            try:
                action = Actions(raw_action)
            except ValueError:
                pass

        position_name = 'SB' if self.hand.active_player == 0 else 'BB'
        self.log(f'{position_name} ({client.name}) {ActionLabels[action]}.')

        return action

    def showdown(self):
        self.log()
        self.log('SHOWDOWN')
        self.show_cards()

    def show_cards(self):
        self.log('SB:', self.hand.sb_cards)
        self.log('BB:', self.hand.bb_cards)
        self.log()
