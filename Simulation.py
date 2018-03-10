# Main simulation class for test setup, generation and analysis

from Relay import *
from Client import *
from Website import *
from HiddenService import *
from User import *


GUARD_RELAYS = 100
MIDDLE_RELAYS = 240
EXIT_RELAYS = 90

TRACKED_GUARD_RELAYS = 3
TRACKED_EXIT_RELAYS = 3

TRACKED_HIDDEN_SERVICES = 1
TRACKED_USERS = 100

CLEARNET_SITES = 20
HIDDEN_SERVICES = 10

SITE_SIZE_AVG = 3000
SITE_BW_AVG = 5000000
USER_BW_AVG = 3000000
RELAY_BW_AVG = 15000000

USERS_NUM = 10000

TIME_TO_RUN = 3000
TOTAL_RUNS = 10

regions = ['Asia', 'Australia', 'Europe', 'North America', 'South America']


def get_region():
    return regions[random.randint(0, len(regions)-1)]


def get_intro_points(relays, ip_num):
    ip_indexes = random.sample(range(0, len(relays)), ip_num)
    return [relays[i] for i in ip_indexes]


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


def generate_hidden_services(relays, guards, middles, exits, hs_num,
                             size_avg, bw_avg, time):
    addresses_to_ips = {}
    hs_list = []
    relay_list = list(relays.values())
    for i in range(hs_num):
        id = 'hs{0}'.format(str(i))
        bw = abs(int(np.random.normal(bw_avg, bw_avg / 10)))
        region = get_region()
        size = abs(int(np.random.normal(size_avg, size_avg/10)))
        ips = get_intro_points(relay_list, 1)
        hs = HiddenService(id, time, bw, region, size, relays, guards, middles, exits, ips)
        addresses_to_ips.update(hs.ips)
        hs_list.append(hs)
    return addresses_to_ips, hs_list


USER_ID_COUNTER = 0


def generate_users(relays, guards, middles, exits, users_num, bw_avg,
                   sites, ips, time, low_guards_no=False, time_range=0):
    users = []
    global USER_ID_COUNTER
    for i in range(USER_ID_COUNTER, USER_ID_COUNTER+users_num):
        id = 'c{0}'.format(str(i))
        bw = abs(int(np.random.normal(bw_avg, bw_avg / 10)))
        region = get_region()
        pos_guards = guards
        if low_guards_no:
            pos_guards = [guards[i] for i in random.sample(range(len(guards)), 3)]
        time += random.randint(0, time_range)
        client = Client(id, time, bw, region, relays, pos_guards, middles, exits, ips)
        user_type = random.randint(1, 6)
        user = User(client, user_type, sites, list(ips.keys()))
        users.append(user)
    USER_ID_COUNTER += users_num
    return users


if __name__ == '__main__':
    guard_num = GUARD_RELAYS
    middle_num = MIDDLE_RELAYS
    exit_num = EXIT_RELAYS
    tracked_guards_num = TRACKED_GUARD_RELAYS
    tracked_exits_num = TRACKED_EXIT_RELAYS
    sites_num = CLEARNET_SITES
    hs_num = HIDDEN_SERVICES
    tracked_users_num = TRACKED_USERS
    users_num = USERS_NUM

    relay_bw = RELAY_BW_AVG
    site_bw = SITE_BW_AVG
    user_bw = USER_BW_AVG

    site_size = SITE_SIZE_AVG

    runs = TOTAL_RUNS

    relays, guards, middles, exits,\
    tracked_guards, tracked_exits = generate_relays(guard_num, middle_num, exit_num,
                                                    tracked_guards_num, tracked_exits_num,
                                                    relay_bw)

    total_time = 0
    for i in range(runs):
        sites = generate_sites(sites_num, site_size, site_bw)

        time = 0
        t_t_r = TIME_TO_RUN
        total_time += t_t_r

        addresses_to_ips, hidden_services = generate_hidden_services(relays,
                                                                     guards, middles,
                                                                     exits, hs_num,
                                                                     site_size, site_bw,
                                                                     time)

        tracked_users = generate_users(relays, guards, middles, exits,
                                       tracked_users_num, user_bw, sites,
                                       addresses_to_ips, time, low_guards_no=True)

        for user in tracked_users:
            while user.client.time < t_t_r:
                user.visit_next()
            # print(user.client.circuit_counter)
        print('GENERATED TRACKED USER TRAFFIC')
        while t_t_r > 0:
            time_for_traffic = min(t_t_r, 600)
            t_t_r -= 600
            guard_users_num = users_num // len(guards)
            for g in tracked_guards:
                guard_users = generate_users(relays, [g], middles, exits,
                                             guard_users_num, user_bw, sites,
                                             addresses_to_ips, time, time_range=600)
                for user in guard_users:
                    while user.client.time < time_for_traffic:
                        user.visit_next()

            exit_users_num = users_num // len(exits)
            for e in tracked_exits:
                exit_users = generate_users(relays, guards, middles, [e],
                                            exit_users_num, user_bw, sites,
                                            addresses_to_ips, time, time_range=600)
                for user in exit_users:
                    user_start_time = user.client.time
                    while user.client.time < user_start_time + time_for_traffic:
                        user.visit_next()
            print('GENERATED TRAFFIC FOR TRACKED EXITS AND GUARDS AT TIME {0}'.format(time))

            time += 600

        tr_user_guard_traffic = {}
        rel_middles= []
        tracked_user_ids = [u.client.id for u in tracked_users]
        for u in tracked_user_ids:
            tr_user_guard_traffic[u] = {}
        for g in tracked_guards:
            for u in tracked_user_ids:
                if u in g.in_traffic:
                    tracked_user_in = g.in_traffic[u]
                    for p in tracked_user_in:
                        if len(p) == 6:
                            m = p[2]
                            latency = get_latency(g.continent, relays[m].continent)
                            if m not in tr_user_guard_traffic[u]:
                                tr_user_guard_traffic[u][m] = []
                            if m not in rel_middles:
                                rel_middles.append(m)
                            packet_send_time = p[1]
                            packet_circuit_id = p[4]
                            packet_circuit_type = p[5]
                            tr_user_guard_traffic[u][m].append((packet_send_time+latency,
                                                                packet_circuit_id,
                                                                packet_circuit_type,
                                                                ))
                    # print(u, tr_user_guard_traffic[u].keys())
        for exit in tracked_exits:
            for m in rel_middles:
                if m in exit.in_traffic:
                    exit.in_traffic[m].sort(key=lambda x: x[0])
                    # print('!!!!!!!!!', exit.in_traffic[m])
        tp, tn, fp, fn = 0, 0, 0, 0
        tp_by_circuit = {
            'General': 0,
            'C-IP':    0,
            'C-RP':    0,
        }
        found_users = []
        for u in tr_user_guard_traffic:
            for m in tr_user_guard_traffic[u]:
                for exit in tracked_exits:
                    if m in exit.in_traffic:
                        latency = get_latency(relays[m].continent, relays[exit.id].continent)
                        dif = latency + 0.0016
                        error = 0.002
                        i_m, i_e = 0, 0
                        cor_found, false_found = 0, 0
                        t_to_mid = tr_user_guard_traffic[u][m]
                        t_in_ex = exit.in_traffic[m]
                        # print(dif, '\n', t_to_mid, '\n', t_in_ex)
                        # print(' ')
                        while i_m < len(t_to_mid) and i_e < len(t_in_ex):
                            m_time = t_to_mid[i_m][0]
                            m_circuit = t_to_mid[i_m][1]
                            m_circuit_type = t_to_mid[i_m][2]
                            e_time = t_in_ex[i_e][0]
                            e_originator = t_in_ex[i_e][1]
                            e_circuit = t_in_ex[i_e][2]
                            if len(t_in_ex[i_e]) > 4:
                                e_originator = t_in_ex[i_e][3]
                                e_circuit = t_in_ex[i_e][4]
                            res = e_time - m_time - dif
                            if res <= error and res >= -1 * error:
                                if m_circuit == e_circuit:
                                    if e_originator not in found_users:
                                        found_users.append(e_originator)
                                    tp += 1
                                    tp_by_circuit[m_circuit_type] += 1
                                    # print(m_time+dif - e_time)
                                else:
                                    fp += 1
                                i_m += 1
                                i_e += 1
                            elif res > error:
                                i_m += 1
                            else:
                                if m_circuit == e_circuit:
                                    print(res)
                                    fn += 1
                                else:
                                    tn += 1
                                i_e += 1
        print('TP: {0}, FP: {1}, TN: {2}, FN: {3}'.format(tp, fp, tn, fn))
        print(tp_by_circuit)
        print(found_users)
    print(total_time)
    # print(len(exit.in_traffic[m]))


