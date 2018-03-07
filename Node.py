# Superclass representing network nodes that provides packet
# sending/receiving and traffic logging

from utils import *

# Time it takes for node to process received packets (read headers,
# decrypt layer etc.)
NODE_PROCESSING_TIME = 0.001


class Node:

    def __init__(self, id, bandwidth, continent, tracked=None):
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
        # Set previous node of packet to be the sender
        packet.last_from = sender.id
        if self.tracked:
            if sender.id not in self.in_traffic:
                self.in_traffic[sender.id] = []
            # Add time of arrival
            self.in_traffic[sender.id].append((packet.creation_time+packet.lived, packet.original_from))
        # Add packet processing time at receiver node to packet total
        # lived time
        packet.lived += NODE_PROCESSING_TIME
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
        prev_send_time = packets[0].creation_time + packets[0].lived
        if self.tracked:
            if destination.id not in self.out_traffic:
                self.out_traffic[destination.id] = []
        for i in range(len(packets)):
            packet = packets[i]
            # packet can only be sent once previous packet has been sent
            time_of_send = max(packet.creation_time+packet.lived, prev_send_time)
            if self.tracked:
                # If current node is not originator of packet, change
                # in traffic from previous sender of packet to
                # contain next hop in circuit and sending time
                if packet.last_from:
                    last_in_traffic = self.in_traffic[packet.last_from]
                    arrival_time = last_in_traffic[-(len(packets)-i)][0]
                    packet_traffic = (arrival_time, time_of_send, destination.id, packet.original_from)
                    last_in_traffic[-(len(packets)-i)] = packet_traffic
                # Add time of arrival to out traffic
                self.out_traffic[destination.id].append(time_of_send)
            packet.lived = time_of_send + latency + packet.size / self.bandwidth - packet.creation_time
            prev_send_time = time_of_send + packet.size / self.bandwidth
            destination.receive_packet(self, packet, circuit=circuit, as_endpoint=to_endpoint)