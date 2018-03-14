# Main simulation class for test setup, generation and analysis

import datetime

from Setup import *
from Relay import *
from Client import *
from Website import *
from HiddenService import *
from User import *


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
                             size_avg, bw_avg, time, low_guards_no=False):
    addresses_to_ips = {}
    hs_list = []
    relay_list = list(relays.values())
    for i in range(hs_num):
        id = 'hs{0}'.format(str(i))
        bw = abs(int(np.random.normal(bw_avg, bw_avg / 10)))
        region = get_region()
        pos_guards = guards
        if low_guards_no:
            pos_guards = [guards[i] for i in random.sample(range(len(guards)), 3)]
        size = abs(int(np.random.normal(size_avg, size_avg/10)))
        ips = get_intro_points(relay_list, 1)
        hs = HiddenService(id, time, bw, region, size, relays, pos_guards, middles, exits, ips)
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
    now = datetime.datetime.now()
    filename = 'results/{0}.res'.format(now)
    res_file = open(filename, 'w')
    env_string =  \
"""GUARD_RELAYS = {0}
MIDDLE_RELAYS = {1}
EXIT_RELAYS = {2}
TRACKED_GUARD_RELAYS = {3}
TRACKED_EXIT_RELAYS = {4}
CLEARNET_SITES = {5}
HIDDEN_SERVICES = {6}
TRACKED_USERS = {7}
USERS_NUM = {8}
RELAY_BW_AVG = {9}
SITE_BW_AVG = {10}
USER_BW_AVG = {11}
SITE_SIZE_AVG = {12}
TOTAL_RUNS = {13}
TIME_TO_RUN = {14}
PREDICTED_SEND_TIME = {15}
ERROR = {16}
LATENCY_VARIATION = {17}\n""".format(GUARD_RELAYS, MIDDLE_RELAYS, EXIT_RELAYS, TRACKED_GUARD_RELAYS,
                               TRACKED_EXIT_RELAYS, CLEARNET_SITES, HIDDEN_SERVICES, TRACKED_USERS,
                               USERS_NUM, RELAY_BW_AVG, SITE_BW_AVG, USER_BW_AVG, SITE_SIZE_AVG,
                               TOTAL_RUNS, TIME_TO_RUN, PREDICTED_SEND_TIME, ERROR, LATENCY_VARIATION)

    print(env_string)
    res_file.write(env_string)

    guard_num = GUARD_RELAYS
    middle_num = MIDDLE_RELAYS
    exit_num = EXIT_RELAYS
    tracked_guards_num = TRACKED_GUARD_RELAYS
    tracked_exits_num = TRACKED_EXIT_RELAYS
    sites_num = CLEARNET_SITES
    hs_num = HIDDEN_SERVICES
    tracked_users_num = TRACKED_USERS
    users_num = USERS_NUM
    circuit_time = CIRCUIT_TIME

    relay_bw = RELAY_BW_AVG
    site_bw = SITE_BW_AVG
    user_bw = USER_BW_AVG

    site_size = SITE_SIZE_AVG

    runs = TOTAL_RUNS

    total_time = 0
    all_tp, all_fp, all_tn, all_fn = 0, 0, 0, 0
    avg_rec, avg_prec = 0, 0
    avg_deanonymise_rate = 0
    avg_site_wait, avg_hs_wait = 0, 0
    for i in range(runs):
        total_site_wait, total_hs_wait, sites_visited, hs_visited = 0, 0, 0, 0
        relays, guards, middles, exits, \
        tracked_guards, tracked_exits = generate_relays(guard_num, middle_num, exit_num,
                                                        tracked_guards_num, tracked_exits_num,
                                                        relay_bw)
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
            total_site_wait += user.client.site_wait_time
            total_hs_wait += user.client.hs_wait_time
            sites_visited += user.client.sites_visited
            hs_visited += user.client.hs_visited
            # print(user.client.circuit_counter)
        print('GENERATED TRACKED USER TRAFFIC')
        while t_t_r > 0:
            time_for_traffic = min(t_t_r, circuit_time)
            t_t_r -= circuit_time
            guard_users_num = users_num // len(guards)
            for g in tracked_guards:
                print('Generating for guard {0}...'.format(g.id))
                guard_users = generate_users(relays, [g], middles, exits,
                                             guard_users_num, user_bw, sites,
                                             addresses_to_ips, time, time_range=circuit_time)
                for user in guard_users:
                    user_start_time = user.client.time
                    while user.client.time < user_start_time + time_for_traffic:
                        user.visit_next()
                    total_site_wait += user.client.site_wait_time
                    total_hs_wait += user.client.hs_wait_time
                    sites_visited += user.client.sites_visited
                    hs_visited += user.client.hs_visited

            exit_users_num = users_num // len(exits)
            for e in tracked_exits:
                print('Generating for exit {0}...'.format(e.id))
                exit_users = generate_users(relays, guards, middles, [e],
                                            exit_users_num, user_bw, sites,
                                            addresses_to_ips, time, time_range=circuit_time)
                for user in exit_users:
                    user_start_time = user.client.time
                    while user.client.time < user_start_time + time_for_traffic:
                        user.visit_next()
                    total_site_wait += user.client.site_wait_time
                    total_hs_wait += user.client.hs_wait_time
                    sites_visited += user.client.sites_visited
                    hs_visited += user.client.hs_visited
            print('GENERATED TRAFFIC FOR TRACKED EXITS AND GUARDS AT TIME {0}'.format(time))

            time += circuit_time

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
        tp_by_circuit_type = {
            'General': 0,
            'C-IP':    0,
            'C-RP':    0,
        }
        deanonymised_circuit_types = {
            'General': 0,
            'C-IP': 0,
            'C-RP': 0
        }
        deanonymised_circuits = []
        found_users = []
        for u in tr_user_guard_traffic:
            for m in tr_user_guard_traffic[u]:
                for exit in tracked_exits:
                    if m in exit.in_traffic:
                        latency = get_latency(relays[m].continent, relays[exit.id].continent)
                        dif = latency + PREDICTED_SEND_TIME
                        error = ERROR
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
                                    if m_circuit not in deanonymised_circuits:
                                        deanonymised_circuits.append(m_circuit)
                                        deanonymised_circuit_types[m_circuit_type] += 1
                                    tp += 1
                                    tp_by_circuit_type[m_circuit_type] += 1
                                else:
                                    fp += 1
                                i_m += 1
                                i_e += 1
                            elif res > error:
                                i_m += 1
                            else:
                                if m_circuit == e_circuit:
                                    fn += 1
                                else:
                                    tn += 1
                                i_e += 1
        totp_str = 'Total packets classified for run analysis: {0}\n'.format(tp+fp+tn+fn)
        cm_str = 'TP: {0}, FP: {1}, TN: {2}, FN: {3}\n'.format(tp, fp, tn, fn)
        rp_str = 'Recall: {0}, Precision: {1}\n'.format(tp/(tp+fn), tp/(tp+fp))
        ctp_str = 'Packets matched by circuit type: {0}\n'.format(tp_by_circuit_type)
        du_str = 'Total deanonymised users - {0} of {1} tracked\n'.format(len(found_users), len(tracked_users))
        cd_str = 'Deanonymised circuits by type: {0}\n'.format(deanonymised_circuit_types)
        swt_str = 'Average wait time for websites: {0}\n'.format(total_site_wait / sites_visited)
        hswt_str = 'Average wait time for hidden services: {0}\n'.format(total_hs_wait / hs_visited)
        res_str = totp_str + cm_str + rp_str + ctp_str + du_str + cd_str + swt_str + hswt_str
        print('\nRESULTS FOR RUN {0} OF {1}:'.format(i+1, runs))
        print(res_str)
        res_file.write('\nRESULTS FOR RUN {0} OF {1}:\n'.format(i + 1, runs))
        res_file.write(res_str)
        all_tp += tp
        all_fp += fp
        all_tn += tn
        all_fn += fn
        avg_prec += tp / (tp + fp)
        avg_rec += tp / (tp + fn)
        avg_deanonymise_rate += len(found_users) / len(tracked_users)
        avg_site_wait += total_site_wait / sites_visited
        avg_hs_wait += total_hs_wait / hs_visited
    totp_str = 'Total packets classified for analysis: {0}\n'.format(all_tp+all_fp+all_tn+all_fn)
    fcm_str = 'TP: {0}, FP: {1}, TN: {2}, FN: {3}\n'.format(all_tp, all_fp, all_tn, all_fn)
    avgrp_str = 'Average Recall: {0}, Average Precision: {1}\n'.format(avg_rec / runs, avg_prec / runs)
    avgdr_str = 'Average pct of deanonymised users out of tracked per run: {0}\n'.format(avg_deanonymise_rate / runs)
    avgsw_str = 'Average wait time for user to visit website: {0}\n'.format(avg_site_wait)
    avghsw_str = 'Average wait time for user to visit website: {0}\n'.format(avg_hs_wait)
    res_str = totp_str + fcm_str + avgrp_str + avgdr_str + avgsw_str + avghsw_str
    print('\nTOTAL RESULTS:')
    print(res_str)
    res_file.write('\nTOTAL RESULTS:\n')
    res_file.write(res_str)
    res_file.close()
    # print(len(exit.in_traffic[m]))


