from .Constant import Constant


class Reservation:
    NR = -1


    def __init__(self, nr: int, day: int, time: int, room: int):
        Reservation.NR = nr
        self.Day = day
        self.Time = time
        self.Room = room


    def __hash__(self) -> int:
        return self.Day * Reservation.NR * Constant.DAY_HOURS + self.Room * Constant.DAY_HOURS + self.Time


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)
            
    def __ne__(self, other):
        return not self.__eq__(other)
        