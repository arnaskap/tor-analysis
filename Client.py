# Client class that simulates end-users of the Tor browser
# connecting to clearnet websites and hidden services

import uuid

from CircuitUser import *


class Client(CircuitUser):

    def __init__(self, id, time, bandwidth, continent, relays, pos_guards,
                 pos_middles, pos_exits, tracked=False):
        super().__init__(id, time, bandwidth, continent, relays,
                         pos_guards, pos_middles, pos_exits, tracked)

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

        # Rendezvous points for hidden services
        self.rps = {}
        # User IDs for hidden services
        self.hs_user_id = {}

    # Get a random relay as the rendezvous point to be used
    def _get_new_rp(self):
        relays_list = list(self.relays)
        return relays_list[random.randint(0, len(relays_list)-1)]

    # Set new circuit as general circuit
    def _establish_general_circuit(self):
        self.general_circuit = self._get_new_circuit(type='General')
        self.time += self.general_circuit.lived

    # Set new circuit as Client to RP circuit for given hidden
    # service
    def _establish_c_rp_circuit(self, hs_address):
        circuit = self._get_new_circuit(type='C-RP', time=self.time)
        self.c_rp_circuit[hs_address] = circuit
        self.time += circuit.lived

    def _nominate_rp(self, hs_address):
        user_id = self.hs_user_id[hs_address]
        out_content = 'RP-C {0} {1}'.format(hs_address, user_id)
        rp_packet = Packet(self.id, self.time, content=out_content)
        rp = self._get_new_rp()
        self.c_rp_circuit[hs_address].send_packets([rp_packet], rp)
        self.time += rp_packet.lived

    def _establish_hs_connection(self, hs_address):
        self._establish_c_rp_circuit(hs_address)
        self._nominate_rp(hs_address)
        self._establish_c_ip_circuit(hs_address)

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
        if not hs_address in self.hs_user_id:
            hs_uid = uuid.uuid4()
            self.hs_user_id[hs_address] = hs_uid

        if not hs_address in self.c_rp_circuit or \
           not self.c_rp_circuit[hs_address].is_running:
