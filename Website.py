# Website class that simulates clearnet website behaviour

import math

from Node import *
from Packet import *


class Website(Node):

    def __init__(self, id, bandwidth, continent, size, tracked=False):
        super().__init__(id, bandwidth, continent, tracked)

        # Website size
        self.size = size

    # Divide website requested content into packet stream
    def _get_site_packet_stream(self, time):
        packets = []
        for i in range(int(math.ceil(self.size / PACKET_SIZE))):
            packets.append(Packet(self.id, time))
        return packets

    # Send website packets back through a circuit
    def _send_website(self, circuit, time):
        packets = self._get_site_packet_stream(time)
        circuit.send_packets_to_startpoint(packets, self)

    # Check for GET requests for website, perform response when found
    def _process_packet(self, sender, packet, circuit=None):
        if circuit and packet.content.startswith('GET'):
            curtime = packet.creation_time + packet.lived
            self._send_website(circuit, curtime)
