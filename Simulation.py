import random
import numpy

from Relay import *

PACKET_SIZE = 586

GUARD_RELAYS = 2050
MIDDLE_RELAYS = 3700
EXIT_RELAYS = 800

UNIVERSAL_DELAY = 2000

CONSUMED_BANDWIDTH_PER_SEC = 14000000000
CIRCUIT_SECONDS = 60.0
AVG_CONCURRENT_USERS = 2750000

def generate_relays(guard_num, middle_num, exit_num, delay):
    guards, middles, exits = [], [], []
    for i in range(guard_num + middle_num + exit_num):
        if i < guard_num:
            guards.append(Relay(i, 'guard', delay))
        elif i < guard_num + middle_num:
            middles.append(Relay(i, 'middle', delay))
        else:
            exits.append(Relay(i,'exit', delay))
    return guards, middles, exits

def generate_requests(guards):
    relay_traffic = {}
    relay_users = {}
    for g in guards:
        relay_traffic[g] = []
        relay_users[g] = []

# lots of assumptions here
def calculate_user_packets_per_circuit(bandwidth_ps, circuit_seconds, users):
    # assumes all bandwidth contains user packets, none for establishing circuits
    # div by 3 since same base packet is processed 3 times by different relays
    packets_ps = bandwidth_ps // (PACKET_SIZE * 3)
    packets_per_circut = packets_ps * circuit_seconds
    avg_user_packets_per_circuit = packets_per_circut // users
    return avg_user_packets_per_circuit

if __name__ == "main":
    guards, middles, exits = generate_relays(GUARD_RELAYS, MIDDLE_RELAYS, EXIT_RELAYS)

    tracked_users = ['127.0.0.1', '255.255.255.255']
    circuits = {}
    for u in tracked_users:
        circuit_guard = guards[random.randint(0, len(guards))]
        circuit_middle = middles[random.randint(0, len(middles))]
        circuit_exit = exits[random.randint(0, len(exits))]
        circuits[u] = (circuit_guard, circuit_middle, circuit_exit)

    owned_guard_indexes = random.sample(range(0, len(guards)), 2)
    owned_exit_indexes = random.sample(range(0, len(exits)), 2)
    owned_guards = [guards[i] for i in owned_guard_indexes]
    owned_exits = [exits[i] for i in owned_exit_indexes]

    for guard in owned_guards:
        generate_requests(guards)
