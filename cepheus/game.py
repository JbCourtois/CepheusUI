from collections import deque
from random import randrange

from cepheus.hand import HandUI
from cepheus.clients import HumanClient, CepheusClient


class Game:
    def __init__(self):
        self.players = deque([HumanClient, CepheusClient])
        self.players.rotate(randrange(2))

    def run(self):
        while True:
            hand = HandUI(*self.players)
            hand.play()
            self.players.rotate(1)
