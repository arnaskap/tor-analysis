from Endpoint import *

PACKET_DELAY = 2.0

class Relay(Endpoint):

    def __init__(self, id, type, delay):
        self.id = id
        self.type = type
        self.delay = delay
        self.traffic = {}
        self.hs_circuits = {}
        self.packets_sent = 0
        self.packets_received = 0

    def add_packet(self, packet):
        user = packet.user_id
        if user in self.traffic:
            self.traffic[user].append(packet)
        else:
            self.traffic[user] = [packet]
        packet.processing_time += self.delay

    def get_all_traffic(self):
        all_traffic = []
        for u in self.traffic:
            all_traffic.extend(self.traffic[u])
        return all_traffic

    def receive_packet(self, packet, make_response, is_response=False):
        self.packets_received += 1
        if make_response:
            return Packet('g'+self.id, PACKET_DELAY)
        elif is_response:
            return packet
        return None

    def send_packet(self, destination, packet, make_response=False, to_endpoint=False):
        self.packets_sent += 1
        if to_endpoint:
            return destination.receive_packet(packet, make_response, sender=self)
        return destination.receive_packet(packet, make_response)

