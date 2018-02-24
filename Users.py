# User class that visits websites based on predefined behaviour types

# Types:
# 1 - visits clearnet sites more often than hidden services, high probability to revisit same sites
# 2 - visits hidden services as often as clearnet sites, high probability to revisit same sites
# 3 - visits hidden services as often as clearnet sites, picks visited websites randomly

class User:

    def __init__(self, client, type):
        self.client = client
        self.type = type

    def visit_next(self):
        if self.type == 1:
            pass
        elif self.type == 2:
            pass
        elif self.type == 3:
            pass
