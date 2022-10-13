# Stores data about classroom
class Room:
    # ID counter used to assign IDs automatically
    _next_room_id = 0

    # Initializes room data and assign ID to room
    def __init__(self, name, lab, number_of_seats):
        # Returns room ID - automatically assigned
        self.Id = Room._next_room_id
        Room._next_room_id += 1
        # Returns name        
        self.Name = name
        # Returns TRUE if room has computers otherwise it returns FALSE
        self.Lab = lab
        # Returns number of seats in room
        self.NumberOfSeats = number_of_seats

    def __hash__(self):
        return hash(self.Id)

    # Compares ID's of two objects which represent rooms
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    # Restarts ID assigments
    @staticmethod
    def restartIDs() -> None:
        Room._next_room_id = 0
