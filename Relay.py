# Relay class that simulates Tor relay behaviour

from Node import *
from Packet import *


class Relay(Node):

    def __init__(self, id, type, bandwidth, continent, tracked=False):
        super().__init__(id, bandwidth, continent, tracked)

        # Type of relay (guard, middle, exit)
        self.type = type
        # Dictionary matching hidden service addresses to HS-IP
        # circuits for hidden services using this relay as an IP
        self.hs_ip_circuits = {}
        # Mapping of C-RP to HS-RP circuits (and vice versa) for
        # clients and hidden services communicating through this
        # relay as an RP
        self.rp_circuits_map = {}
        self.user_counter = 0

    def _process_packet(self, sender, packet, circuit=None):
        curtime = packet.creation_time + packet.lived
        in_content = packet.split(' ')
        packet_type = in_content[0]
        if packet_type.startswith('IP'):
            hs_address = in_content[1]
            rp_id = in_content[2]
            if hs_address in self.hs_ip_circuits:
                hs_ip_circuit = self.hs_ip_circuits[hs_address]
                user_id = self.user_counter
                self.user_counter += 1
                out_content = 'RP-establish {0} {1} {2}'.format(rp_id, user_id, hs_address)
                packet = Packet(self.id, curtime, content=out_content)
                hs_ip_circuit.send_packets_to_startpoint([packet], self)

        if packet_type.startswith('RP-data'):
            pass


    def use_as_intro_point(self, hs_hash, circuit):
        self.hs_ip_circuits[hs_hash] = circuit

    def use_as_rendezvous_point(self, hs_hash, circuit):
        self.hs_rp_circuits[hs_hash] = circuit
