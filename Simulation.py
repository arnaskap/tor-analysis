import random
import numpy as np

from Relay import *
from Client import *
from Website import *
from HiddenService import *


GUARD_RELAYS = 12
MIDDLE_RELAYS = 24
EXIT_RELAYS = 9

TRACKED_GUARD_RELAYS = 2
TRACKED_EXIT_RELAYS = 3

TRACKED_HIDDEN_SERVICES = 1
TRACKED_USERS = 1

CLEARNET_SITES = 20
HIDDEN_SERVICES = 10

SITE_SIZE_AVG = 3000
SITE_BW_AVG = 50000
USER_BW_AVG = 30000
RELAY_BW_AVG = 150000

USERS_PER_RELAY = 10


regions = ['Asia', 'Australia', 'Europe', 'North America', 'South America']

def get_region():
    return regions[random.randint(0, len(regions)-1)]

def generate_relays(guard_num, middle_num, exit_num, tr_guards, tr_exits, relay_bw):
    guards, middles, exits = [], [], []
    relays = {}
    tracked_guards, tracked_exits = [], []
    all_relay_num = guard_num + middle_num + exit_num
    guard_avg_bw = relay_bw * guard_num / all_relay_num
    middle_avg_bw = relay_bw * middle_num / all_relay_num
    exit_avg_bw = relay_bw * exit_num / all_relay_num
    for i in range(guard_num):
        id = 'g{0}'.format(str(i))
        bw = abs(int(np.random.normal(guard_avg_bw, guard_avg_bw/10)))
        region = get_region()
        tracked = False
        if tr_guards > 0:
            tracked = True
            tr_guards -= 1
        relay = Relay(id, 'guard', bw, region, tracked=tracked)
        guards.append(relay)
        relays[id] = relay
        if tracked:
            tracked_guards.append(relay)
    for i in range(middle_num):
        id = 'm{0}'.format(str(i))
        bw = abs(int(np.random.normal(middle_avg_bw, middle_avg_bw/10)))
        region = get_region()
        relay = Relay(id, 'middle', bw, region)
        middles.append(relay)
        relays[id] = relay
    for i in range(exit_num):
        id = 'e{0}'.format(str(i))
        bw = abs(int(np.random.normal(exit_avg_bw, exit_avg_bw/10)))
        region = get_region()
        tracked = False
        if tr_exits > 0:
            tracked = True
            tr_exits -= 1
        relay = Relay(id, 'exit', bw, region, tracked=tracked)
        exits.append(relay)
        relays[id] = relay
        if tracked:
            tracked_exits.append(relay)
    return relays, guards, middles, exits, tracked_guards, tracked_exits

def generate_sites(sites_num, size_avg, bw_avg):
    sites = []
    for i in range(sites_num):
        id = 'ws{0}'.format(str(i))
        bw = abs(int(np.random.normal(bw_avg, bw_avg / 10)))
        region = get_region()
        size = abs(int(np.random.normal(size_avg, size_avg/10)))
        sites.append(Website(id, bw, region, size))
    return sites

def generate_hidden_services(hs_num, relays):
    for i in range(hs_num):
        id = 'hs{0}'.format(str(hs_num))
        bw =
        region = get_region()
        size =

    hs = HiddenService('hs1', 240000, 'Asia', 3500, relays, [guard2], [middle2], [exit2], [ip])
    return ips


if __name__ == '__main__':
    guard_num = GUARD_RELAYS
    middle_num = MIDDLE_RELAYS
    exit_num = EXIT_RELAYS
    tracked_guards_num = TRACKED_GUARD_RELAYS
    tracked_exits_num = TRACKED_EXIT_RELAYS
    sites_num = CLEARNET_SITES
    hs_num = HIDDEN_SERVICES

    relay_bw = RELAY_BW_AVG
    site_bw = SITE_BW_AVG

    site_size = SITE_SIZE_AVG

    relays, guards, middles, exits,\
    tracked_guards, tracked_exits = generate_relays(guard_num, middle_num, exit_num,
                                                    tracked_guards_num, tracked_exits_num,
                                                    relay_bw)

    sites = generate_sites(sites_num, site_bw, site_size)
    hidden_services = generate_hidden_services(hs_num, relays, guards, middles, exits)
    generate_users()

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
