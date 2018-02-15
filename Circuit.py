from Packet import *

# Different type circuit max lifetimes
# Hidden service to intro point
HS_IP_LIFETIME = 3600
# Hidden service to rendezvous point
HS_RP_LIFETIME = 600
# Client to intro point
C_IP_LIFETIME = 600 # usually closes within a few seconds, but max lifetime can be longer
# Client to rendezvous point
C_RP_LIFETIME = 600
# General circuit
GENERAL_LIFETIME = 600

# Placeholder time taken for packet to be sent
PACKET_DELAY = 2.0


class Circuit:

    def __init__(self, startpoint, started_at, type, *relays):
        self.startpoint = startpoint
        self.started_at = started_at
        self.type = type
        self.lived = 0
        self.is_running = False
        if relays[0].type == 'guard' and relays[len(relays)-1].type == 'exit':
            self.circuit = [self.startpoint] + relays
        else:
            raise Exception('Circuit type mismatch')

        # Set the lifetime of the circuit based on its type
        if self.type == 'HS-IP':
            self.lifetime = HS_IP_LIFETIME
        elif self.type == 'HS-RP':
            self.lifetime = HS_RP_LIFETIME
        elif self.type == 'C-IP':
            self.lifetime = C_IP_LIFETIME
        elif self.type =='C-RP':
            self.lifetime = C_RP_LIFETIME
        else:
            self.lifetime = GENERAL_LIFETIME

        self._establish_circuit()

    # Send a packet from the start point through the circuit to specified endpoint
    def send_packets(self, packets, endpoint):
        if self.is_running:
            for i in range(0, len(self.circuit)-1):
                self.circuit[i].send_packets(self.circuit[i+1], packets)
            self.circuit[len(self.circuit)-1].send_packets(endpoint, packets, circuit=self.circuit)
            self.lived += packets[len(packets)-1].processing_time
            # self.startpoint.send_packet(self.guard, packet)
            # self.guard.send_packet(self.middle, packet)
            # self.middle.send_packet(self.exit, packet)
            # resp_packet = self.exit.send_packet(endpoint, packet, make_response=True, to_endpoint=True)
            # self.exit.send_packet(self.middle, resp_packet)
            # self.middle.send_packet(self.guard, resp_packet)
            # self.guard.send_packet(self.startpoint, resp_packet, to_endpoint=True)
            # self.lived += packet.processing_time + resp_packet.processing_time
            if self.lived >= self.lifetime:
                self._close_circuit()

    def send_response_packets(self, packets, endpoint):
        if self.is_running:
            endpoint.send_packets(self.circuit[len(self.circuit)-1], packets)
            for i in range(len(self.circuit)-1, 0, -1):
                self.circuit[i].send_packets(self.circuit[i-1], packets)
            self.lived += packets[len(packets) - 1].processing_time
            if self.lived >= self.lifetime:
                self._close_circuit()

    # Initialize circuit by sending init packets to circuit relays
    def _establish_circuit(self):
        for i in range(1, len(self.circuit)):
            init_packet = Packet(self.startpoint.id, self.started_at+self.lived,
                                 type='INIT_{0}_relay'.format(str(i)))
            for j in range(i):
                self.circuit[j].send_packet(init_packet, self.circuit[j+1])
            self.lived += init_packet.processing_time
            init_confirmed_packet = Packet(self.circuit[i].id, self.started_at+self.lived,
                                           type='INITED_{0}_relay'.format(str(i)))
            for j in range(i, 0, -1):
                self.circuit[j].send_packet(init_confirmed_packet, self.circuit[j-1])
            self.lived += init_confirmed_packet.processing_time

        # init_guard_packet = Packet('INIT_GUARD', PACKET_DELAY)
        # guard_initialised = self.startpoint.send_packet(init_guard_packet, self.guard, response=True)
        # self.guard.send_packet(guard_initialised, self.startpoint)
        #
        # init_middle_packet = Packet('INIT_MIDDLE', PACKET_DELAY)
        # self.startpoint.send_packet(init_middle_packet, self.guard)
        # middle_initialised = self.guard.send_packet(init_middle_packet, self.middle, response=True)
        # self.middle.send_packet(middle_initialised, self.guard)
        # self.guard.send_packet(middle_initialised, self.startpoint)
        #
        # init_exit_packet = Packet('INIT_EXIT', PACKET_DELAY)
        # self.startpoint.send_packet(init_exit_packet, self.guard)
        # self.guard.send_packet(init_exit_packet, self.middle)
        # exit_initialised = self.middle.send_packet(init_exit_packet, self.exit, response=True)
        # self.exit.send_packet(exit_initialised, self.middle)
        # self.middle.send_packet(exit_initialised, self.guard)
        # self.guard.send_packet(exit_initialised, self.startpoint)

        self.is_running = True

    # Close the circuit
    def _close_circuit(self):
        self.is_running = False