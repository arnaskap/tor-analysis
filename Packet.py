# Tor packets typically have a size of 586 bytes
PACKET_SIZE=586


class Packet:

    def __init__(self, user_id, creation_time, type='DATA'):
        self.original_from = user_id
        self.creation_time = creation_time
        self.lived = 0
        self.type = type
        self.size = PACKET_SIZE
