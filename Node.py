# Network node class providing packet sending/receiving and traffic
# logging

from Packet import *

PACKET_DELAY = 2.0

class Node:

    def __init__(self, id, type, delay, tracked=False):
        self.id = id
        self.type = type
        self.delay = delay
        self.tracked = tracked
        self.out_traffic = {}
        self.in_traffic = {}

    def add_packet(self, packet):
        if self.tracked:
            u_from = packet.user_id
            if u_from not in self.in_traffic:
                self.in_traffic[u_from] = []
            # Add time of arrival
            self.in_traffic[u_from].append(packet.creation_time+packet.processing_time)
        packet.processing_time += self.delay

    def get_all_traffic(self):
        all_traffic = []
        for u in self.traffic:
            all_traffic.extend(self.traffic[u])
        return all_traffic

    def receive_packet(self, packet, make_response, sender=None):
        self.add_packet(packet)
        if make_response:
            resp_packet = Packet('g'+self.id, PACKET_DELAY)
            return self.send_packet(sender, resp_packet, is_response=True)
        return None

    def send_packet(self, destination, packet, make_response=False, is_response=False):
        if destination not in self.out_traffic:
            self.out_traffic[destination] = {}
        self.out_traffic[destination].append(packet.creation_time+packet.processing_time)
        return destination.receive_packet(packet, make_response, is_response)
