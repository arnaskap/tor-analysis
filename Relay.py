from Packet import *

class Relay:

    def __init__(self, id, type, delay):
        self.id = id
        self.type = type
        self.delay = delay
        self.traffic = {}

    def add_packet(self, packet):
        user = packet.user_id
        if user in self.traffic:
            self.traffic[user].append(packet)
        else:
            self.traffic[user] = [packet]
        return Packet(packet.user_id, packet.time+self.delay)

    def get_all_traffic(self):
        all_traffic = []
        for u in self.traffic:
            all_traffic.extend(self.traffic[u])
        return all_traffic
