import random

from Endpoint import *
from Circuit import *


class Client(Endpoint):

    def __init__(self, id, type, delay, pos_guards, pos_middles, pos_exits):

        # Possible guard, middle and exit relay lists for this user
        self.pos_guards = pos_guards # Typically only 3 guards possible for a user every 2-3 months
        self.pos_middles = pos_middles
        self.pos_exits = pos_exits

        # Possible circuits a user can be using at once

        # Can have one active general circuit for visiting clearnet
        # sites
        self.general_circuit = None
        # Can have one active Client - Intro Point circuit for every
        # different hidden service establishing an RP with
        self.c_ip_circuit = {}
        # Can have one active Client - Rendezvous Point circuit for
        # every different hidden service being visited
        self.c_rp_circuit = {}
        super().__init__(id, type, delay)

    # Selects guard, middle and exit relays for some circuit at random
    # Note: realistic relay selection is weighted by bandwidth
    def _select_relays_for_circuit(self):
        circuit_guard = self.pos_guards[random.randint(0, len(self.pos_guards) - 1)]
        circuit_middle = self.pos_middles[random.randint(0, len(self.pos_middles) - 1)]
        circuit_exit = self.pos_exits[random.randint(0, len(self.pos_exits) - 1)]
        return circuit_guard, circuit_middle, circuit_exit

    def send_

    # Emulates packet sending for visiting a specified clearnet website
    def visit_clearnet_site(self, site):
        # Create new general circuit if required
        if not self.general_circuit or not self.general_circuit.is_running:
            self.general_circuit = Circuit(self, 'General', *self._select_relays_for_circuit())
        self.general_circuit.send_packet(Packet('{0} GET {1}'.format(self.id, site.id)), site)

    def visit_hidden_service(self, hs):
        if hs not in