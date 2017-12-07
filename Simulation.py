import random
import numpy as np

from Relay import *
from Packet import *

PACKET_SIZE = 586
UNIVERSAL_DELAY = 2.0
CIRCUIT_SECONDS = 60.0

# GUARD_RELAYS = 2050
# MIDDLE_RELAYS = 3700
# EXIT_RELAYS = 800
#
# CONSUMED_BANDWIDTH_PER_SEC = 14000000000
# AVG_CONCURRENT_USERS = 2750000
GUARD_RELAYS = 205
MIDDLE_RELAYS = 370
EXIT_RELAYS = 80

CONSUMED_BANDWIDTH_PER_SEC = 140000000
AVG_CONCURRENT_USERS = 275000


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


def generate_circuits(users_num, guards, middles, exits):
    circuits = {}
    for user in range(users_num):
        circuit_guard = guards[random.randint(0, len(guards)-1)]
        circuit_middle = middles[random.randint(0, len(middles)-1)]
        circuit_exit = exits[random.randint(0, len(exits)-1)]
        circuits[user] = (circuit_guard, circuit_middle, circuit_exit)
    return circuits


def generate_user_packets(circuit, user, avg_packets_sent, circuit_seconds):
    total_packets = abs(int(np.random.normal(avg_packets_sent, 300.0)))
    packet_times = np.random.uniform(low=0.0, high=circuit_seconds, size=(total_packets,))
    for t in packet_times:
        p1 = Packet(user, t)
        p2 = circuit[0].add_packet(p1)
        p3 = circuit[1].add_packet(p2)
        circuit[2].add_packet(p3)


def generate_relay_traffic(circuits, owned_guards, owned_exits, avg_packets_sent, circuit_seconds):
    for u in circuits:
        if circuits[u][0] not in owned_guards and circuits[u][2] not in owned_exits:
            continue
        generate_user_packets(circuits[u], u, avg_packets_sent, circuit_seconds)


# lots of assumptions here
def calculate_user_packets_per_circuit(bandwidth_ps, circuit_seconds, users):
    # assumes all bandwidth contains user packets, none for establishing circuits
    # div by 3 since same base packet is processed 3 times by different relays
    packets_ps = bandwidth_ps // (PACKET_SIZE * 3)
    packets_per_circut = packets_ps * circuit_seconds
    avg_user_packets_per_circuit = packets_per_circut // users
    return avg_user_packets_per_circuit


def set_user_guards_owned(users, circuits, owned_guards):
    for u in users:
        circuits[u] = (owned_guards[random.randint(0, len(owned_guards)-1)], circuits[u][1], circuits[u][2])


def set_user_exits_owned(users, circuits, owned_exits):
    for u in users:
        circuits[u] = (circuits[u][0], circuits[u][1], (owned_exits[random.randint(0, len(owned_exits) - 1)]))


if __name__ == '__main__':
    guards, middles, exits = generate_relays(GUARD_RELAYS, MIDDLE_RELAYS, EXIT_RELAYS, UNIVERSAL_DELAY)

    tracked_users = [10, 60]
    circuits = generate_circuits(AVG_CONCURRENT_USERS, guards, middles, exits)

    owned_guard_indexes = random.sample(range(0, len(guards)-1), 2)
    owned_exit_indexes = random.sample(range(0, len(exits)-1), 2)
    owned_guards = [guards[i] for i in owned_guard_indexes]
    owned_exits = [exits[i] for i in owned_exit_indexes]
    avg_packets_per_user = calculate_user_packets_per_circuit(CONSUMED_BANDWIDTH_PER_SEC, CIRCUIT_SECONDS, AVG_CONCURRENT_USERS)
    print(avg_packets_per_user)
    set_user_guards_owned(tracked_users, circuits, owned_guards)
    set_user_exits_owned(tracked_users, circuits, owned_exits)
    generate_relay_traffic(circuits, owned_guards, owned_exits, avg_packets_per_user, CIRCUIT_SECONDS)
    tracked_users_in_owned_guards = []
    tracked_users_in_owned_exits = []
    for u in tracked_users:
        if circuits[u][0] in owned_guards:
            tracked_users_in_owned_guards.append((u, circuits[u][0]))
            print('User %d used guard %s is tracked' % (u, circuits[u][0].id))
        if circuits[u][2] in owned_exits:
            tracked_users_in_owned_exits.append((u, circuits[u][2]))
            print('User %d used exit %s is tracked' % (u, circuits[u][2].id))
    for ug in tracked_users_in_owned_guards:
        user, guard = ug[0], ug[1]
        user_traffic = guard.traffic[user]
        traffic_map = {}
        predicted_exit = None
        for t in user_traffic:
            traffic_map[t.time] = False
        for exit in owned_exits:
            cur_traffic_map = traffic_map.copy()
            true_count = 0
            all_exit_traffic = exit.get_all_traffic()
            for packet in all_exit_traffic:
                guard_time = packet.time - 4.0
                if traffic_map.get(guard_time, None) is False:
                    true_count += 1
                    traffic_map[guard_time] = True
            print(true_count, len(traffic_map))
            if true_count == len(user_traffic):
                predicted_exit = exit
                break
        if predicted_exit is not None:
            print('Predicted exit for tracked user %d is exit %s' % (user, predicted_exit.id))
            print(circuits[user][2] == predicted_exit)
        else:
            print('Tracked user %d not found in owned exits' % user)
            print(circuits[user][2] not in owned_exits)

