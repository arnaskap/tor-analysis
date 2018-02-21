# Client class that simulates end-users of the Tor browser
# connecting to clearnet websites and hidden services

import uuid

from CircuitUser import *


class Client(CircuitUser):

    def __init__(self, id, time, bandwidth, continent, relays, pos_guards,
                 pos_middles, pos_exits, ips, tracked=False):
        super().__init__(id, time, bandwidth, continent, relays,
                         pos_guards, pos_middles, pos_exits, tracked)

        # Possible circuits a user can be using at once

        # Can have one active general circuit for visiting clearnet
        # sites
        self.general_circuit = None
        # Can have one active Client - Intro Point circuit for every
        # different hidden service establishing an RP with
        self.c_ip_circuits = {}
        # Can have one active Client - Rendezvous Point circuit for
        # every different hidden service being visited
        self.c_rp_circuits = {}

        # Hidden service address to introduction point map
        self.ips = ips
        # Rendezvous points for hidden services
        self.rps = {}
        # User IDs for hidden services
        self.hs_user_ids = {}

    # Get a random relay as the rendezvous point to be used
    def _get_new_rp(self):
        relays_list = list(self.relays)
        return relays_list[random.randint(0, len(relays_list)-1)]

    # Set new circuit as general circuit
    def _establish_general_circuit(self):
        circuit = self._get_new_circuit(type='General')
        self.time += circuit.lived
        self.general_circuit = circuit

    def _establish_c_ip_circuit(self, hs_address):
        circuit = self._get_new_circuit(type='C-RP', time=self.time)
        self.time += circuit.lived
        self.c_ip_circuits[hs_address] = circuit

    # Set new circuit as Client to RP circuit for given hidden
    # service
    def _establish_c_rp_circuit(self, hs_address, rp_id):
        circuit = self._get_new_circuit(type='C-RP', time=self.time, exclude=[rp_id])
        self.time += circuit.lived
        self.c_rp_circuits[hs_address] = circuit

    # Send request to HS intro point asking to start communication
    # through specified rendezvous point
    def _send_to_ip(self, hs_address, rp_id):
        ip = self.ips[hs_address]
        user_id = self.hs_user_ids[hs_address]
        out_content = 'IP {0} {1} {2}'.format(hs_address, rp_id, user_id)
        packet = Packet(self.id, self.time, content=out_content)
        self.c_ip_circuits[hs_address].send_packets([packet], ip)

    # Send first packet to RP through established C-RP circuit,
    # nominating it for HS communication
    def _nominate_rp(self, hs_address, rp):
        user_id = self.hs_user_ids[hs_address]
        out_content = 'RP-C {0} {1}'.format(hs_address, user_id)
        rp_packet = Packet(self.id, self.time, content=out_content)
        self.c_rp_circuits[hs_address].send_packets([rp_packet], rp)
        self.time += rp_packet.lived

    def _establish_hs_connection(self, hs_address):
        rp = self._get_new_rp()
        self._establish_c_rp_circuit(hs_address, rp.id)
        self._nominate_rp(hs_address, rp)
        self.rps[hs_address] = rp
        self._establish_c_ip_circuit(hs_address)
        self._send_to_ip(hs_address, rp.id)

    def _process_packet(self, sender, packet, circuit=None):
        in_content = packet.split(' ')
        packet_type = in_content[0]
        if packet_type.startswith('RP-confirm') or \
           packet_type.startswith('RP-data'):
            self.time = packet.creation_time + packet.lived

    # Emulates packet sending for visiting a specified clearnet website
    def visit_clearnet_site(self, site):
        # Create new general circuit if required
        if not self.general_circuit or not self.general_circuit.is_running:
            self._establish_general_circuit()
        # GET request packet for specified site
        get_packet = Packet(self.id, self.time,
                            content='GET {0}'.format(site.id))
        self.general_circuit.send_packets([get_packet], site)
        self.time += get_packet.lived

    # Emulates process of establishing connection to hidden service
    # and making requests / receiving responses from it
    def visit_hidden_service(self, hs_address):
        if not hs_address in self.hs_user_ids:
            hs_uid = uuid.uuid4()
            self.hs_user_ids[hs_address] = hs_uid

        if not hs_address in self.c_rp_circuits or \
           not self.c_rp_circuits[hs_address].is_running:
            self._establish_hs_connection(hs_address)

        user_id = self.hs_user_ids[hs_address]
        c_rp_circuit = self.c_rp_circuits[hs_address]
        rp = self.rps[hs_address]
        out_content = 'RP-GET {0} {1}'.format(hs_address, user_id)
        packet = Packet(self.id, self.time, content=out_content)
        c_rp_circuit.send_packets([packet], rp)
