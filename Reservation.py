import Constant


class Reservation:
    def __init__(self, nr: int, day: int, time: int, room: int):
        self.Nr = nr
        self.Day = day
        self.Time = time
        self.Room = room
        self._index = self.Day * self.Nr * Constant.Constant.DAY_HOURS + self.Room * Constant.Constant.DAY_HOURS + self.Time

    @property
    def index(self) -> int:
        return self._index
