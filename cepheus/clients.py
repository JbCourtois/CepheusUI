from abc import ABCMeta, abstractmethod
from random import random

import requests


class Client(metaclass=ABCMeta):
    name = 'BaseClient'

    @abstractmethod
    def __init__(self, position, cards):
        pass

    @abstractmethod
    def get_action(self, hand_state):
        pass


class HumanClient(Client):
    name = 'Human'

    def __init__(self, position, cards):
        print(f'You are {position}.')
        print('Your cards:', cards)

    def get_action(self, hand_state):
        return input('Your action? (F)old / (C)all / (R)aise')


class CepheusClient(Client):
    name = 'Cepheus'

    def __init__(self, position, cards):
        cards.sort(key=lambda c: c.rank, reverse=True)
        self.cards = cards.to_cepheus()

    def get_action(self, hand_state):
        response = requests.get(
            'http://poker.srv.ualberta.ca/query',
            params={'queryString': hand_state},
            stream=True,
        )
        return self.parse_response(response)

    def parse_response(self, response):
        hands = response.iter_lines(chunk_size=50, decode_unicode=True)
        next(hands)  # Skip header

        for line in hands:
            hand, *probs = line.decode().split(' ')
            if hand == self.cards:
                return self.act(*map(float, probs[:3]))

        raise ValueError('Bad hand:', self.cards)

    def act(self, p_fold, p_call, p_raise):
        prob = random()
        if prob < p_fold:
            return 'F'

        prob -= p_fold
        if prob < p_call:
            return 'C'

        return 'R'
