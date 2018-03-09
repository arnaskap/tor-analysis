# Circuit class used that abstracts the process of establishing
# active circuits and sending or receiving packets through them

from Packet import *

# Different type circuit max lifetimes

# General circuit
GENERAL_LIFETIME = 600
# Client to intro point, usually closes within a few seconds, but
# max lifetime can be longer
C_IP_LIFETIME = 600
# Client to rendezvous point
C_RP_LIFETIME = 600
# Hidden service to intro point
HS_IP_LIFETIME = 3600
# Hidden service to rendezvous point
HS_RP_LIFETIME = 600


class Circuit:

    def __init__(self, id, startpoint, started_at, type, relays):
        self.id = id
        # The initiator node of the circuit
        self.startpoint = startpoint
        # Time at which circuit was started
        self.started_at = started_at
        # Type of circuit
        self.type = type
        # Time that circuit has been active for
        self.lived = 0
        # Flag that says if the circuit is active
        self.is_running = False

        # If given relays are of appropriate types, set the circuit
        # to the startpoint appended with given relays in the
        # appropriate order
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

        # Start the circuit
        self._establish_circuit()

        # print(startpoint.id, type, [i.id for i in self.circuit])

    # Send a stream of packets from the start point through the
    # circuit to a specified endpoint
    def send_packets(self, packets, endpoint):
        if self.is_running:
            for i in range(0, len(self.circuit)-1):
                self.circuit[i].send_packets(self.circuit[i+1], packets, circuit=self)
            self.circuit[len(self.circuit)-1].send_packets(endpoint, packets, to_endpoint=True, circuit=self)
            self.lived += packets[len(packets)-1].lived
            if self.lived >= self.lifetime:
                self._close_circuit()

    # Send a stream of packets as a response from the endpoint
    # through the circuit to the startpoint
    def send_packets_to_startpoint(self, packets, endpoint):
        if self.is_running:
            endpoint.send_packets(self.circuit[len(self.circuit)-1], packets, circuit=self)
            for i in range(len(self.circuit)-1, 1, -1):
                self.circuit[i].send_packets(self.circuit[i-1], packets, circuit=self)
            self.circuit[1].send_packets(self.circuit[0], packets, to_endpoint=True)
            self.lived += packets[len(packets) - 1].lived
            if self.lived >= self.lifetime:
                self._close_circuit()

    # Initialize circuit by sending init packets to circuit relays
    def _establish_circuit(self):
        # For every relay, an initialisation packet must be sent
        # through the partly initialised circuit and back to the
        # startpoint
        for i in range(1, len(self.circuit)):
            init_packet = Packet(self.startpoint.id, self.started_at+self.lived,
                                 content='INIT_{0}_relay'.format(str(i)))
            for j in range(i):
                self.circuit[j].send_packets(self.circuit[j+1], [init_packet],
                                             circuit=self)
            self.lived += init_packet.lived
            init_confirmed_packet = Packet(self.circuit[i].id, self.started_at+self.lived,
                                           content='INITED_{0}_relay'.format(str(i)))
            for j in range(i, 0, -1):
                self.circuit[j].send_packets(self.circuit[j-1], [init_confirmed_packet],
                                             circuit=self)
            self.lived += init_confirmed_packet.lived
        self.is_running = True

    # Close the circuit
    def _close_circuit(self):
        self.is_running = False
