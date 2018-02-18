# Hidden service class, simulating behaviour of hidden services on
# the Tor network

from CircuitUser import *


class HiddenService(CircuitUser):

    def __init__(self, id, time, type, bandwidth, continent,
                 pos_guards, pos_middles, pos_exits, intro_points,
                tracked=False):
        super().__init__(id, time, type, bandwidth, continent, pos_guards,
                         pos_middles, pos_exits, tracked)

        self._setup_intro_points(intro_points)
        # Can have one active Hidden Service - Intro Point circuit
        # for every Intro Point used for this service
        self.hs_ip_circuits = {}
        # Can have one active Hidden Service - Rendezvous Point
        # circuit for every different client visiting the service
        self.hs_rp_circuits = {}

    # Function for initial setup of introduction point circuits
    def _setup_intro_points(self, intro_points):
        for ip in intro_points:
            hash = self._get_new_hash()
            circuit = self._get_new_circuit(type='HS-IP')
            self.hs_ip_circuits[hash] = circuit
            ip.use_as_intro_point(hash, circuit)
