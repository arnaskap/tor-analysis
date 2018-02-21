# Superclass representing network nodes that provides packet
# sending/receiving and traffic logging

from utils import *

# Time it takes for node to process received packets (read headers,
# decrypt layer etc.)
NODE_PROCESSING_TIME = 0.001


class Node:

    def __init__(self, id, bandwidth, continent, tracked):
        # ID of the node (equivalent of IP address)
        self.id = id
        # Bandwidth of the node
        self.bandwidth = bandwidth
        # Flag that says if the node is tracked by the attacker
        self.tracked = tracked
        # Continent that node is on, used for latency
        self.continent = continent
        # Dictionary that matches node IDs to outwards traffic times
        # from this node
        self.out_traffic = {}
        # Dictionary that matches node IDs to inwards traffic times
        # from this node
        self.in_traffic = {}

    # Receive a packet
    def receive_packet(self, sender, packet, circuit=None, as_endpoint=False):
        # print(sender.id, self.id, packet.creation_time+packet.lived)
        # Add packet processing time at receiver node to packet total
        # lived time
        packet.lived += NODE_PROCESSING_TIME
        if self.tracked:
            # print(sender.id, self.id, packet.creation_time + packet.lived)
            if sender.id not in self.in_traffic:
                self.in_traffic[sender.id] = []
            # Add time of arrival
            self.in_traffic[sender.id].append(packet.creation_time+packet.lived)
        # Packet content analysis to be performed if endpoint
        # receives the packet
        if as_endpoint:
            self._process_packet(sender, packet, circuit=circuit)

    # Class to be overridden by children for endpoint packet
    # processing
    def _process_packet(self, sender, packet, circuit=None):
        pass

    # Send a stream of packets directly to a destination
    def send_packets(self, destination, packets, to_endpoint=False, circuit=None):
        latency = get_latency(self.continent, destination.continent)
        # The further a packet is in the stream, the more time it
        # takes to start sending it
        size_sent = 0
        if self.tracked:
            if destination.id not in self.out_traffic:
                self.out_traffic[destination.id] = []
        for packet in packets:
            if self.tracked:
                # Add time of arrival
                self.out_traffic[destination.id].append(packet.creation_time+packet.lived)
            packet.lived += latency + (packet.size + size_sent) / self.bandwidth
            size_sent += packet.size
            destination.receive_packet(self, packet, circuit=circuit, as_endpoint=to_endpoint)