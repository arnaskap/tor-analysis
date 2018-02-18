# Superclass that provides shared functionality of active Tor users,
# namely clients and hidden services

import random

from Node import *
from Circuit import *


class CircuitUser(Node):

    def __init__(self, id, time, type, bandwidth, continent,
                 pos_guards, pos_middles, pos_exits, tracked=False):
        super().__init__(id, type, bandwidth, continent, tracked)

        # Possible guard, middle and exit relay lists for this user

        # Typically only 3 guards possible for a user every 2-3 months
        self.pos_guards = pos_guards
        self.pos_middles = pos_middles
        self.pos_exits = pos_exits

        # Global time
        self.time = time

    # Selects guard, middle and exit relays for some circuit at random
    # Note: realistic relay selection is weighted by bandwidth
    def _select_relays_for_circuit(self):
        circuit_guard = self.pos_guards[random.randint(0, len(self.pos_guards) - 1)]
        circuit_middle = self.pos_middles[random.randint(0, len(self.pos_middles) - 1)]
        circuit_exit = self.pos_exits[random.randint(0, len(self.pos_exits) - 1)]
        return circuit_guard, circuit_middle, circuit_exit

    def _get_new_circuit(self, type='General'):
        return Circuit(self, type, self._select_relays_for_circuit())
