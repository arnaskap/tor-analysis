# Simulation environment definition file

import numpy as np
import random

GUARD_RELAYS = 30
MIDDLE_RELAYS = 40
EXIT_RELAYS = 20

CLEARNET_SITES = 400
HIDDEN_SERVICES = 80

SITE_SIZE_AVG = 5000
SITE_BW_AVG = 5000000
USER_BW_AVG = 3000000
RELAY_BW_AVG = 15000000

USERS_NUM = 500

TIME_TO_RUN = 600
TOTAL_RUNS = 10
CIRCUIT_TIME = 600

TRACKED_GUARD_RELAYS = 3
TRACKED_EXIT_RELAYS = 3

TRACKED_HIDDEN_SERVICES = 10
TRACKED_USERS = 30

PREDICTED_SEND_TIME = 0.0016
ERROR = 0.03

LATENCY_VARIATION = 0.015

# Correlation attack defence measures
CIRCUIT_MIDDLE_NO = 1
DELAY_CAP = 0

# Circuit fingerprinting attack defence measures
C_HS_EQUAL_PACKETS = False
MAX_SPLIT = 3 # set to 0 for no sub-stream splits
HS_DELAY_CAP = 1

regions = ['Asia', 'Australia', 'Europe', 'North America', 'South America']

# Latency dictionary between continents, values in seconds
LATENCY = {
    ('Asia', 'Asia'): 0.01,
    ('Asia', 'Australia'): 0.13,
    ('Asia', 'Europe'): 0.22,
    ('Asia', 'North America'): 0.16,
    ('Asia', 'South America'): 0.28,
    ('Australia', 'Asia'): 0.13,
    ('Australia', 'Australia'): 0.01,
    ('Australia', 'Europe'): 0.3,
    ('Australia', 'North America'): 0.19,
    ('Australia', 'South America'): 0.32,
    ('Europe', 'Asia'): 0.22,
    ('Europe', 'Australia'): 0.3,
    ('Europe', 'Europe'): 0.01,
    ('Europe', 'North America'): 0.12,
    ('Europe', 'South America'): 0.19,
    ('North America', 'Asia'): 0.16,
    ('North America', 'Australia'): 0.19,
    ('North America', 'Europe'): 0.12,
    ('North America', 'North America'): 0.01,
    ('North America', 'South America'): 0.14,
    ('South America', 'Asia'): 0.28,
    ('South America', 'Australia'): 0.32,
    ('South America', 'Europe'): 0.19,
    ('South America', 'North America'): 0.14,
    ('South America', 'South America'): 0.01,
}


# Return latency between locations
def get_latency(c1, c2):
    st_latency = LATENCY[(c1, c2)]
    latency = abs(np.random.normal(st_latency, LATENCY_VARIATION))
    return latency

def get_region():
    return regions[random.randint(0, len(regions)-1)]
