# Client class that simulates end-users of the Tor browser
# connecting to clearnet websites and hidden services

from CircuitUser import *


class Client(CircuitUser):

    def __init__(self, id, time, bandwidth, continent, pos_guards, pos_middles,
                 pos_exits, tracked=False):
        super().__init__(id, time, bandwidth, continent, pos_guards,
                         pos_middles, pos_exits, tracked)

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

    # Set new circuit as general circuit for this client
    def _establish_general_circuit(self):
        self.general_circuit = self._get_new_circuit(type='General')

    def _establish_c_rp_circuit(self, hs_address):
        self._visit_hs_ip(hs_address)

    # Emulates packet sending for visiting a specified clearnet website
    def visit_clearnet_site(self, site):
        # Create new general circuit if required
        if not self.general_circuit or not self.general_circuit.is_running:
            self._establish_general_circuit()
        # GET request packet for specified site
        get_packet = Packet(self.id, self.time,
                            content='GET {0}'.format(site.id))
        self.general_circuit.send_packets(get_packet)
        self.time += get_packet.lived

    def visit_hidden_service(self, hs_address):
        if not hs_address in self.c_rp_circuit or \
           not self.c_rp_circuit[hs_address].is_running:
            self._establish_c_rp_circuit(hs_address)
