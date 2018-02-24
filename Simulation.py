import random
import numpy as np

from Relay import *
from Client import *
from Website import *
from HiddenService import *


GUARD_RELAYS = 12
MIDDLE_RELAYS = 24
EXIT_RELAYS = 9

CLEARNET_SITES = 20
HIDDEN_SERVICES = 10

SITE_SIZE_AVG = 3000
SITE_BW_AVG = 50000
USER_BW_AVG = 30000
RELAY_BW_AVG = 150000

USERS_PER_RELAY = 10


regions = ['Asia', 'Australia', 'Europe', 'North America', 'South America']


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

def get_region():
    return regions[random.randint(0, len(regions)-1)]


def generate_hidden_services(relays, amount):
    count = 1
    for count in range(amount+1):
        id = 'hs{0}'.format(str(count))
        bw =
        region = get_region()
        size =

    hs = HiddenService('hs1', 240000, 'Asia', 3500, relays, [guard2], [middle2], [exit2], [ip])
    return ips


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

# def connec


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
    # guards, middles, exits = generate_relays(GUARD_RELAYS, MIDDLE_RELAYS, EXIT_RELAYS, UNIVERSAL_DELAY)
    time = 0
    exit = Relay('e1', 'exit', 200000, 'North America', tracked=True)
    guard = Relay('g1', 'guard', 100000, 'Asia', tracked=True)
    middle= Relay('m1', 'middle', 50000, 'Europe', tracked=True)
    guard2 = Relay('g2', 'guard', 100000, 'Asia', tracked=True)
    middle2 = Relay('m2', 'middle', 50000, 'Europe', tracked=True)
    exit2 = Relay('e2', 'exit', 200000, 'North America', tracked=True)
    ip = Relay('e2', 'exit', 120000, 'North America')
    middle3 = Relay('m3', 'middle', 80000, 'Europe', tracked=True)

    rs = [guard, guard2, middle, middle2, exit, exit2, ip, middle3]
    relays = {}
    for r in rs:
        relays[r.id] = r
    site = Website('w1', 150000, 'Australia', 2000)
    hs = HiddenService('hs1', 240000, 'Asia', 3500, relays, [guard2], [middle2], [exit2], [ip])

    ips = hs.ips
    user = Client('u1', 0, 75000, 'Europe', relays, [guard], [middle], [exit], ips)
    user.visit_clearnet_site(site)
    hs_address = list(ips.keys())[0]
    user.visit_hidden_service(hs_address)
    user.visit_hidden_service(hs_address)
    print(guard.in_traffic)
    print(guard.out_traffic)
