# User class that visits websites based on predefined behaviour types

# Types:
# 1 - visits clearnet sites more often than hidden services, high probability to revisit same sites, visits often
# 2 - visits hidden services as often as clearnet sites, high probability to revisit same sites, visits often
# 3 - visits hidden services as often as clearnet sites, picks visited websites randomly, visits often
# 4 - visits clearnet sites more often than hidden services, high probability to revisit same sites, visits rarely
# 5 - visits hidden services as often as clearnet sites, high probability to revisit same sites, visits rarely
# 6 - visits hidden services as often as clearnet sites, picks visited websites randomly, visits rarely


import random
import numpy as np


class User:

    def __init__(self, client, type, sites, hidden_services):
        self.client = client
        self.type = type
        self.sites = sites
        self.hidden_services = hidden_services
        self.visited_sites = []
        self.visited_hidden_services = []

    def _visit_site_by_prob(self, pr_hs, pr_new):
        visit_hs_chance = random.randint(1, pr_hs)
        visit_same_chance = random.randint(1, pr_new)
        if visit_hs_chance < pr_hs:
            if visit_same_chance < pr_new and self.visited_sites:
                which_site = random.randint(0, len(self.visited_sites) - 1)
                site_to_visit = self.visited_sites[which_site]
                self.client.visit_clearnet_site(site_to_visit)
            else:
                which_site = random.randint(0, len(self.sites) - 1)
                site_to_visit = self.sites[which_site]
                self.client.visit_clearnet_site(site_to_visit)
                if site_to_visit not in self.visited_sites:
                    self.visited_sites.append(site_to_visit)
        else:
            if visit_same_chance < pr_new and self.visited_hidden_services:
                which_hs = random.randint(0, len(self.visited_hidden_services) - 1)
                hs_to_visit = self.visited_hidden_services[which_hs]
                self.client.visit_hidden_service(hs_to_visit)
            else:
                which_hs = random.randint(0, len(self.hidden_services) - 1)
                hs_to_visit = self.hidden_services[which_hs]
                self.client.visit_hidden_service(hs_to_visit)
                if hs_to_visit not in self.visited_hidden_services:
                    self.visited_hidden_services.append(hs_to_visit)

    def visit_next(self):
        if self.type < 4:
            self.client.time += abs(np.random.normal(5, 2.5))
        else:
            self.client.time += abs(np.random.normal(15, 5))

        if self.type == 1 or self.type == 4:
           self._visit_site_by_prob(5, 10)
        elif self.type == 2 or self.type == 5:
            self._visit_site_by_prob(2, 10)
        elif self.type == 3 or self.type == 6:
            self._visit_site_by_prob(2, 2)
