from Packet import *

class Relay:

    def __init__(self, id, type, delay):
        self.id = id
        self.type = type
        self.delay = delay
        self.traffic = {}

    def addPacket(self, user, packet):
        if user in self.traffic:
            self.traffic[user].append(packet)
        else:
            self.traffic[user] = [packet]
        return Packet(packet.ip, packet.time+self.delay)