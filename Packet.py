class Packet:

    def __init__(self, user_id, creation_time, type='DATA'):
        self.original_from = user_id
        self.creation_time = creation_time
        self.processing_time = 0
        self.type = type
