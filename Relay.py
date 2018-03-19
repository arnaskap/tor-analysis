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
        self.hs_rp_circuits = {}
        self.c_rp_circuits = {}

        self.data_packets = []

    def _process_packet(self, sender, packet, circuit=None):
        curtime = packet.creation_time + packet.lived
        in_content = packet.content.split(' ')
        packet_type = in_content[0]

        if packet_type  == 'IP':
            hs_address = in_content[1]
            rp_id = in_content[2]
            user_id = in_content[3]
            out_content = 'IP-confirm {0} {1}'.format(rp_id, hs_address)
            response_packet = Packet(self.id, curtime, content=out_content)
            circuit.send_packets_to_startpoint([response_packet], self)
            curtime = response_packet.creation_time + response_packet.lived
            if hs_address in self.hs_ip_circuits:
                hs_ip_circuit = self.hs_ip_circuits[hs_address]
                out_content = 'RP-establish {0} {1} {2}'.format(rp_id, user_id, hs_address)
                packet = Packet(self.id, curtime, content=out_content)
                hs_ip_circuit.send_packets_to_startpoint([packet], self)

        elif packet_type == 'RP-C':
            hs_address = in_content[1]
            user_id = in_content[2]
            self.c_rp_circuits[(user_id, hs_address)] = circuit

        elif packet_type == 'RP-HS':
            hs_address = in_content[1]
            user_id = in_content[2]
            self.hs_rp_circuits[(user_id, hs_address)] = circuit
            c_rp_circuit = self.c_rp_circuits[(user_id, hs_address)]
            out_content = 'RP-confirm {0} {1}'.format(hs_address, user_id)
            packet = Packet(self.id, curtime, content=out_content)
            c_rp_circuit.send_packets_to_startpoint([packet], self)

        elif packet_type == 'RP-GET':
            hs_address = in_content[1]
            user_id = in_content[2]
            hs_rp_circuit = self.hs_rp_circuits[(user_id, hs_address)]
            out_content = 'RP-GET {0} {1}'.format(hs_address, user_id)
            packet = Packet(self.id, curtime, content=out_content)
            hs_rp_circuit.send_packets_to_startpoint([packet], self)

        elif packet_type =='RP-data':
            hs_address = in_content[1]
            user_id = in_content[2]
            out_content = 'RP-data {0} {1}'.format(hs_address, user_id)
            packet = Packet(self.id, curtime, content=out_content)
            self.data_packets.append(packet)

        elif packet_type == 'RP-finish-data':
            hs_address = in_content[1]
            user_id = in_content[2]
            out_content = 'RP-data {0} {1}'.format(hs_address, user_id)
            packet = Packet(self.id, curtime, content=out_content)
            self.data_packets.append(packet)
            c_rp_circuit = self.c_rp_circuits[(user_id, hs_address)]
            c_rp_circuit.send_packets_to_startpoint(self.data_packets, self)
            self.data_packets = []

    # # function used to emulate functionality of a relay in a
    # # circuit, receiving a packet and sending it
    # def receive_and_send(self):

    def use_as_intro_point(self, hs_hash, circuit):
        self.hs_ip_circuits[hs_hash] = circuit
