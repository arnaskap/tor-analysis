import random
import numpy as np

from Relay import *
from Packet import *

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


def generate_circuits(users_num):
    circuits = {}
    for user in users_num:
        circuit_guard = guards[random.randint(0, len(guards))]
        circuit_middle = middles[random.randint(0, len(middles))]
        circuit_exit = exits[random.randint(0, len(exits))]
        circuits[user] = (circuit_guard, circuit_middle, circuit_exit)
    return circuits


def generate_user_packets(circuits, user, avg_packets_sent, circuit_seconds):
    total_packets = int(np.random.normal(avg_packets_sent, 300.0))
    packet_times = np.random.uniform(low=0.0, high=circuit_seconds, size=(total_packets,))
    for t in packet_times:
        p1 = Packet(user, t)
        p2 = circuits[0].addPacket(p1)
        p3 = circuits[1].addPacket(p2)
        circuits[2].addPacket(p3)



def generate_relay_traffic(circuits, owned_guards, owned_exits, avg_packets_sent, circuit_seconds):
    for u in circuits:
        if circuits[u][0] not in owned_guards and circuits[u][2] not in owned_exits:
            pass
        generate_user_packets(circuits, u, avg_packets_sent, circuit_seconds)


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

    tracked_users = [10, 60]
    circuits = generate_circuits(AVG_CONCURRENT_USERS, guards, middles, exits)

    owned_guard_indexes = random.sample(range(0, len(guards)), 2)
    owned_exit_indexes = random.sample(range(0, len(exits)), 2)
    owned_guards = [guards[i] for i in owned_guard_indexes]
    owned_exits = [exits[i] for i in owned_exit_indexes]
    avg_packets_per_user = calculate_user_packets_per_circuit(CONSUMED_BANDWIDTH_PER_SEC, CIRCUIT_SECONDS, AVG_CONCURRENT_USERS)
    generate_relay_traffic(circuits, owned_guards, owned_exits, avg_packets_per_user, CIRCUIT_SECONDS)
    for guard in owned_guards:
        print(guard.id, len(guard.traffic))


