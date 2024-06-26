# Superclass representing network nodes that provides packet
# sending/receiving and traffic logging

from Setup import *

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

        self.circuit_traffic = {}
        self.circuit_sequence = {}
        self.circuit_packet_count = {}

    # Receive a packet
    def receive_packet(self, sender, packet, circuit=None, as_endpoint=False, response=False):
        # Set previous node of packet to be the sender
        packet.last_from = sender.id
        circuit_id = '' if not circuit else circuit.id
        circuit_type = '' if not circuit else circuit.type
        if self.tracked:
            if sender.id not in self.in_traffic:
                self.in_traffic[sender.id] = []
            if not response and (not as_endpoint or not packet.to_mm):
                if sender.id not in self.circuit_traffic:
                    self.circuit_traffic[sender.id] = {}
                if sender.id not in self.circuit_sequence:
                    self.circuit_sequence[sender.id] = {}
                if sender.id not in self.circuit_packet_count:
                    self.circuit_packet_count[sender.id] = {}
                if circuit_id not in self.circuit_traffic[sender.id]:
                    self.circuit_traffic[sender.id][circuit_id] = []
                if circuit_id not in self.circuit_sequence[sender.id]:
                    self.circuit_sequence[sender.id][circuit_id] = ''
                if circuit_id not in self.circuit_packet_count[sender.id]:
                    self.circuit_packet_count[sender.id][circuit_id] = [0, 0]

            # Add time of arrival
            packet_info = (packet.creation_time+packet.lived, packet.original_from,
                           circuit_id, circuit_type)
            self.in_traffic[sender.id].append(packet_info)
            if not response and (not as_endpoint or not packet.to_mm):
                packet_type = packet.content.split(' ')[0]
                packet_info = (packet.creation_time+packet.lived, packet.original_from,
                               circuit_id, circuit_type, packet_type)
                self.circuit_traffic[sender.id][circuit_id].append(packet_info)
                seq_string = '-1'
                packet_idx = 1
                c_seq = self.circuit_sequence[sender.id][circuit_id]
                if len(c_seq) < 24:
                    self.circuit_sequence[sender.id][circuit_id] = c_seq + seq_string
                self.circuit_packet_count[sender.id][circuit_id][packet_idx] += 1

        # Add packet processing time at receiver node to packet total
        # lived time
        proc_time = abs(int(np.random.normal(NODE_PROCESSING_TIME, NODE_PROCESSING_TIME)))
        packet.lived += proc_time
        # Packet content analysis to be performed if endpoint
        # receives the packet
        if as_endpoint:
            self._process_packet(sender, packet, circuit=circuit)

    # Class to be overridden by children for endpoint packet
    # processing
    def _process_packet(self, sender, packet, circuit=None):
        pass

    # Send a stream of packets directly to a destination
    def send_packets(self, destination, packets, to_endpoint=False, circuit=None, response=False):
        latency = get_latency(self.continent, destination.continent)
        prev_send_time = packets[0].creation_time + packets[0].lived
        # Circuit info of packets later used for traffic confirmation
        # of attacks
        circuit_id = '' if not circuit else circuit.id
        circuit_type = '' if not circuit else circuit.type
        if self.tracked:
            if destination.id not in self.out_traffic:
                self.out_traffic[destination.id] = []
            if response and (not to_endpoint or not packets[0].to_mm):
                # if destination.id not in self.circuit_traffic:
                #     self.circuit_traffic[destination.id] = {}
                if destination.id not in self.circuit_sequence:
                    self.circuit_sequence[destination.id] = {}
                if destination.id not in self.circuit_packet_count:
                    self.circuit_packet_count[destination.id] = {}
                # if circuit_id not in self.circuit_traffic[destination.id]:
                #     self.circuit_traffic[destination.id][circuit_id] = []
                if circuit_id not in self.circuit_sequence[destination.id]:
                    self.circuit_sequence[destination.id][circuit_id] = ''
                if circuit_id not in self.circuit_packet_count[destination.id]:
                    self.circuit_packet_count[destination.id][circuit_id] = [0, 0]
        for i in range(len(packets)):
            # Get random delay for every packet as defence measure
            delay = random.uniform(0, DELAY_CAP)
            packet = packets[i]
            # packet can only be sent once previous packet has been sent
            time_of_send = max(packet.creation_time+packet.lived, prev_send_time)
            time_of_send += delay
            if self.tracked:
                # If current node is not originator of packet, change
                # in traffic from previous sender of packet to
                # contain next hop in circuit and sending time
                if packet.last_from:
                    last_in_traffic = self.in_traffic[packet.last_from]
                    arrival_time = last_in_traffic[-(len(packets)-i)][0]
                    packet_traffic = (arrival_time, time_of_send, destination.id,
                                      packet.original_from, circuit_id,
                                      circuit_type)
                    last_in_traffic[-(len(packets)-i)] = packet_traffic
                # Add time of arrival to out traffic
                if response and (not to_endpoint or not packet.to_mm):
                    # print(self.id, destination.id)
                    seq_string = '+1'
                    packet_idx = 0
                    c_seq = self.circuit_sequence[destination.id][circuit_id]
                    if len(c_seq) < 24:
                        self.circuit_sequence[destination.id][circuit_id] = c_seq + seq_string
                    self.circuit_packet_count[destination.id][circuit_id][packet_idx] += 1
                self.out_traffic[destination.id].append(time_of_send)
            packet.lived = time_of_send + latency + packet.size / self.bandwidth - packet.creation_time
            prev_send_time = time_of_send + packet.size / self.bandwidth
            destination.receive_packet(self, packet, circuit=circuit, as_endpoint=to_endpoint,
                                       response=response)