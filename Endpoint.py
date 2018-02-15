from Packet import *

class Endpoint:

    def __init__(self, id, type, delay, tracked=False):
        self.id = id
        self.type = type
        self.delay = delay
        self.tracked = tracked
        self.out_traffic = {}
        self.in_traffic = {}

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

    def receive_packet(self, packet, make_response, sender=None):
        self.packets_received += 1
        if make_response:
            resp_packet = Packet('g'+self.id, PACKET_DELAY)
            return self.send_packet(sender, resp_packet, is_response=True)
        return None

    def send_packet(self, destination, packet, make_response=False, is_response=False):
        if destination not in self.out_traffic:
            self.out_traffic[destination] = {}
        self.out_traffic[destination].append()
        self.packets_sent += 1
        return destination.receive_packet(packet, make_response, is_response)
