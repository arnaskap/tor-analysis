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

    def _process_packet(self, sender, packet, circuit=None):
        curtime = packet.creation_time + packet.lived
        in_content = packet.split(' ')
        packet_type = in_content[0]
        if packet_type.startswith('IP'):
            hs_address = in_content[1]
            rp_id = in_content[2]
            if hs_address in self.hs_ip_circuits:
                out_content = 'RP {0} {1}'
                packet = Packet(self.id, curtime, content='RP')
        if packet_type.startswith('RP'):
            pass

    def use_as_intro_point(self, hs_hash, circuit):
        self.hs_ip_circuits[hs_hash] = circuit

    def use_as_rendezvous_point(self, hs_hash, circuit):
        self.hs_rp_circuits[hs_hash] = circuit
