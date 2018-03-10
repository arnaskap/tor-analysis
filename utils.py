import numpy as np

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
    return LATENCY[(c1, c2)]