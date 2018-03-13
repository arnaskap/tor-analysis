# Packet class that contains information necessary for packet
# processing and traffic logging

# Tor packets typically have a size of 586 bytes (512 Tor cell wrapped
# with IP and TCP info)
PACKET_SIZE=586


# Possible packet types:
# Data
# IP
# RP-C
# RP-confirm
# RP-data
# fill in later

class Packet:

    def __init__(self, user_id, creation_time, content='DATA'):
        # original sender of packet
        self.original_from = user_id
        # previous sender of packet
        self.last_from = None
        self.circuit = None
        self.circuit_type = None
        self.creation_time = creation_time
        self.lived = 0
        self.content = content
        self.size = PACKET_SIZE
