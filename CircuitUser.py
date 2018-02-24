# Superclass that provides shared functionality of active Tor users,
# namely clients and hidden services

import random

from Node import *
from Circuit import *


class CircuitUser(Node):

    def __init__(self, id, bandwidth, continent, relays,
                 pos_guards, pos_middles, pos_exits, tracked=False):
        super().__init__(id, bandwidth, continent, tracked)

        # Map of relay IDs to relay objects
        self.relays = relays

        # Possible guard, middle and exit relay lists for this user

        # Typically only 3 guards possible for a user every 2-3 months
        self.pos_guards = pos_guards
        self.pos_middles = pos_middles
        self.pos_exits = pos_exits

    # Selects guard, middle and exit relays for some circuit at random
    # Note: realistic relay selection is weighted by bandwidth
    def _select_relays_for_circuit(self, exclude=None):
        circuit_guard = self.pos_guards[random.randint(0, len(self.pos_guards) - 1)]
        if exclude:
            while circuit_guard in exclude:
                circuit_guard = self.pos_guards[random.randint(0, len(self.pos_guards) - 1)]
        circuit_middle = self.pos_middles[random.randint(0, len(self.pos_middles) - 1)]
        if exclude:
            while circuit_middle in exclude:
                circuit_middle = self.pos_middles[random.randint(0, len(self.pos_middles) - 1)]
        circuit_exit = self.pos_exits[random.randint(0, len(self.pos_exits) - 1)]
        if exclude:
            while circuit_exit in exclude:
                circuit_exit = self.pos_exits[random.randint(0, len(self.pos_exits) - 1)]
        return [circuit_guard, circuit_middle, circuit_exit]

    def _get_new_circuit(self, type='General', time=None, exclude=None):
        if not time:
            time = self.time
        return Circuit(self, time, type, self._select_relays_for_circuit(exclude=exclude))
