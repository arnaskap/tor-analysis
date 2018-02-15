import random

from Node import *
from Circuit import *


class Client(Node):

    def __init__(self, id, time, type, bandwidth, continent,
                 pos_guards, pos_middles, pos_exits, tracked=False):
        # Possible guard, middle and exit relay lists for this user

        # Typically only 3 guards possible for a user every 2-3 months
        self.pos_guards = pos_guards
        self.pos_middles = pos_middles
        self.pos_exits = pos_exits

        # Global time
        self.time = time

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

        super().__init__(id, type, bandwidth, continent, tracked)

    # Selects guard, middle and exit relays for some circuit at random
    # Note: realistic relay selection is weighted by bandwidth
    def _select_relays_for_circuit(self):
        circuit_guard = self.pos_guards[random.randint(0, len(self.pos_guards) - 1)]
        circuit_middle = self.pos_middles[random.randint(0, len(self.pos_middles) - 1)]
        circuit_exit = self.pos_exits[random.randint(0, len(self.pos_exits) - 1)]
        return circuit_guard, circuit_middle, circuit_exit

    def _establish_general_circuit(self):
        self.general_circuit = Circuit(self, 'General', self._select_relays_for_circuit())

    def _establish_c_rp_circuit(self, hs_hash):


    # Emulates packet sending for visiting a specified clearnet website
    def visit_clearnet_site(self, site):
        # Create new general circuit if required
        if not self.general_circuit or not self.general_circuit.is_running:
            self._establish_general_circuit()
        # GET request packet for specified site
        get_packet = Packet(self.id, self.time,
                            type='GET {0} {1}'.format(self.id, site.id))
        self.general_circuit.send_packets(get_packet)
        self.time += get_packet.lived

    def visit_hidden_service(self, hs_hash):
        if not hs_hash in self.c_rp_circuit or \
           not self.c_rp_circuit[hs_hash].is_running:
            self._establish_c_rp_circuit(hs_hash)
