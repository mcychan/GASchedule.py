from .Constant import Constant


# Reads configuration file and stores parsed objects
class Criteria:
    weights = [0, 0.5, 0.5, 0, 0]

    # check for room overlapping of classes
    @staticmethod
    def isRoomOverlapped(slots, reservation, dur):
        reservation_index = hash(reservation)
        cls = slots[reservation_index: reservation_index + dur]
        return any(True for slot in cls if len(slot) > 1)

    # does current room have enough seats
    @staticmethod
    def isSeatEnough(r, cc):
        return r.NumberOfSeats >= cc.NumberOfSeats

    # does current room have computers if they are required
    @staticmethod
    def isComputerEnough(r, cc):
        return (not cc.LabRequired) or (cc.LabRequired and r.Lab)

    # check overlapping of classes for professors and student groups
    @staticmethod
    def isOverlappedProfStudentGrp(slots, cc, numberOfRooms, timeId):
        po = go = False

        dur = cc.Duration
        for i in range(numberOfRooms, 0, -1):
            # for each hour of class
            for j in range(timeId, timeId + dur):
                cl = slots[j]
                for cc1 in cl:
                    if cc != cc1:
                        # professor overlaps?
                        if not po and cc.professorOverlaps(cc1):
                            po = True
                        # student group overlaps?
                        if not go and cc.groupsOverlap(cc1):
                            go = True
                        # both type of overlapping? no need to check more
                        if po and go:
                            return po, go

            timeId += Constant.DAY_HOURS
        return po, go
