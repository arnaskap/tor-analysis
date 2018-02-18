# Hidden service class, simulating behaviour of hidden services on
# the Tor network

import hashlib

from CircuitUser import *


class HiddenService(CircuitUser):

    def __init__(self, id, time, bandwidth, continent, pos_guards, pos_middles,
                 pos_exits, intro_points, tracked=False):
        super().__init__(id, time, bandwidth, continent, pos_guards,
                         pos_middles, pos_exits, tracked)

        self._setup_intro_points(intro_points)
        # Can have one active Hidden Service - Intro Point circuit
        # for every Intro Point used for this service
        self.hs_ip_circuits = {}
        # Can have one active Hidden Service - Rendezvous Point
        # circuit for every different client visiting the service
        self.hs_rp_circuits = {}

        # Hash address counter for ensuring unique hashes
        self.hash_counter = 0

    # Function for generating new hashes to be used as HS addresses
    def _get_new_hash(self, ip_id):
        hash_string = '{0}-{1}-{2}'.format(self.id, ip_id, str(self.hash_counter))
        hash = hashlib.sha1(hash_string.encode('utf-8')).hexdigest()
        address = '{0}.onion'.format(hash)
        return address

    # Function for initial setup of introduction point circuits
    def _setup_intro_points(self, intro_points):
        for ip in intro_points:
            address = self._get_new_hash(ip.id)
            circuit = self._get_new_circuit(type='HS-IP')
            self.hs_ip_circuits[address] = circuit
            ip.use_as_intro_point(address, circuit)
            self.hash_counter += 1
