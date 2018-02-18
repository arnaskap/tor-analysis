from Node import *
from Circuit import *


class Relay(Node):

    def __init__(self, id, type, bandwidth, continent, tracked=False):
        self.hs_ip_circuits = {}
        self.hs_rp_circuits = {}

        super().__init__(id, type, bandwidth, continent, tracked)

    def _process_packet(self, sender, packet):
        if packet.content

    def use_as_intro_point(self, hs_hash, circuit):
        self.hs_ip_circuits[hs_hash] = circuit

    def use_as_rendezvous_point(self, hs_hash, circuit):
        self.hs_rp_circuits[hs_hash] = circuit
