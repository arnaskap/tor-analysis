# Hidden service class, simulating behaviour of hidden services on
# the Tor network

import hashlib
import math

from CircuitUser import *


class HiddenService(CircuitUser):

    def __init__(self, id, time, bandwidth, continent, size, relays, pos_guards,
                 pos_middles, pos_exits, intro_points, tracked=False):
        super().__init__(id, bandwidth, continent, relays,
                         pos_guards, pos_middles, pos_exits, tracked)

        # Can have one active Hidden Service - Intro Point circuit
        # for every Intro Point used for this service
        self.hs_ip_circuits = {}
        # Can have one active Hidden Service - Rendezvous Point
        # circuit for every different client visiting the service
        self.hs_rp_circuits = {}
        # Maps users to their used rendezvous points
        self.user_rp = {}
        # Size of website
        self.size = size
        self.ips = {}
        # Hash address counter for ensuring unique hashes
        self.hash_counter = 0
        self.time = time
        self._setup_intro_points(intro_points)

    # Function for generating new hashes to be used as HS addresses
    def _get_new_hash(self, ip_id):
        hash_string = '{0}-{1}-{2}'.format(self.id, ip_id, str(self.hash_counter))
        hash = hashlib.sha1(hash_string.encode('utf-8')).hexdigest()
        address = '{0}.onion'.format(hash)
        return address

    # Divide website requested content into packet stream
    def _get_site_packet_stream(self, hs_address, user_id, time):
        packets = []
        out_content = 'RP-data {0} {1}'.format(hs_address, user_id)
        for i in range(int(math.ceil(self.size / PACKET_SIZE))-1):
            packets.append(Packet(self.id, time, content=out_content))
        out_content = 'RP-finish-data {0} {1}'.format(hs_address, user_id)
        packets.append(Packet(self.id, time, content=out_content))
        return packets

    # Function for initial setup of introduction point circuits
    def _setup_intro_points(self, intro_points):
        for ip in intro_points:
            address = self._get_new_hash(ip.id)
            circuit = self._get_new_circuit(type='HS-IP')
            self.hs_ip_circuits[address] = circuit
            self.ips[address] = ip
            ip.use_as_intro_point(address, circuit)
            self.hash_counter += 1

    # Establishes an HS-RP circuit for a given user and proposed RP
    def _setup_rp_circuit(self, rp, address, user_id, time):
        circuit = self._get_new_circuit(type='HS-RP', time=time)
        self.hs_rp_circuits[(address, user_id)] = circuit
        rp.hs_rp_circuits[(address, user_id)] = circuit
        self.user_rp[user_id] = rp

    # Send website packets back through a circuit
    def _send_website(self, hs_address, user_id, time):
        packets = self._get_site_packet_stream(hs_address, user_id, time)
        hs_rp_circuit = self.hs_rp_circuits[(hs_address, user_id)]
        rp = self.user_rp[user_id]
        hs_rp_circuit.send_packets(packets, rp)

    def _process_packet(self, sender, packet, circuit=None):
        curtime = packet.creation_time + packet.lived
        in_content = packet.content.split(' ')
        packet_type = in_content[0]
        if packet_type.startswith('RP-establish'):
            rp_id = in_content[1]
            user_id = in_content[2]
            hs_address = in_content[3]
            rp_relay = self.relays[rp_id]
            self._setup_rp_circuit(rp_relay, hs_address, user_id, curtime)
            curtime += self.hs_rp_circuits[(hs_address, user_id)].lived
            out_content = 'RP-HS {0} {1}'.format(hs_address, user_id)
            packet = Packet(self.id, curtime, content=out_content)
            self.hs_rp_circuits[(hs_address, user_id)].send_packets([packet], rp_relay)
        elif packet_type.startswith('RP-GET'):
            hs_address = in_content[1]
            user_id = in_content[2]
            self._send_website(hs_address, user_id, curtime)

