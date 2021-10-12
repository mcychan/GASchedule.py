from Constant import Constant


class Reservation:
    def __init__(self, nr: int, day: int, time: int, room: int):
        self.Nr = nr
        self.Day = day
        self.Time = time
        self.Room = room
        self._index = self.Day * self.Nr * Constant.DAY_HOURS + self.Room * Constant.DAY_HOURS + self.Time

    def __hash__(self) -> int:
        return self._index

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        else:
            return False
            
    def __ne__(self, other):
        return not self.__eq__(other)
        