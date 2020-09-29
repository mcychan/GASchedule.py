import Constant
import Reservation
import functools
from collections import defaultdict
from random import randrange


# Schedule chromosome
class Schedule:
    # Initializes chromosomes with configuration block (setup of chromosome)
    def __init__(self, configuration):
        self._configuration = configuration
        # Fitness value of chromosome        
        self._fitness = 0

        # Time-space slots, one entry represent one hour in one classroom
        slots_length = Constant.Constant.DAYS_NUM * Constant.Constant.DAY_HOURS * self._configuration.numberOfRooms
        self._slots = [[] for _ in range(slots_length)]

        # Class table for chromosome
        # Used to determine first time-space slot used by class
        self._classes = defaultdict(Reservation.Reservation)

        # Flags of class requirements satisfaction
        self._criteria = (self._configuration.numberOfCourseClasses * Constant.Constant.DAYS_NUM) * [False]

    def copy(self, c, setup_only):
        if not setup_only:
            self._configuration = c.configuration
            # copy code
            self._slots = c.slots
            self._classes = c.classes

            # copy flags of class requirements
            self._criteria = c.criteria

            # copy fitness
            self._fitness = c.fitness
            return self

        return Schedule(c.configuration)

    # Makes new chromosome with same setup but with randomly chosen code
    def makeNewFromPrototype(self):
        # make new chromosome, copy chromosome setup
        new_chromosome = self.copy(self, True)
        new_chromosome_slots = new_chromosome._slots
        new_chromosome_classes = new_chromosome._classes

        # place classes at random position
        classes = self._configuration.courseClasses
        nr = self._configuration.numberOfRooms
        DAYS_NUM = Constant.Constant.DAYS_NUM
        DAY_HOURS = Constant.Constant.DAY_HOURS + 1
        for c in classes:
            # determine random position of class
            dur = c.Duration
            day = randrange(32768) % DAYS_NUM
            room = randrange(32768) % nr
            time = randrange(32768) % (DAY_HOURS - dur)
            reservation = Reservation.Reservation(nr, day, time, room)
            reservation_index = reservation.index

            # fill time-space slots, for each hour of class
            for slot in new_chromosome_slots[reservation_index: reservation_index + dur]:
                slot.append(c)

            # insert in class table of chromosome
            new_chromosome_classes[c] = reservation

        new_chromosome.calculateFitness()
        return new_chromosome

    @functools.lru_cache(maxsize=256)
    # Performs crossover operation using to chromosomes and returns pointer to offspring
    def crossover(self, parent2, numberOfCrossoverPoints, crossoverProbability):
        # check probability of crossover operation
        if randrange(32768) % 100 > crossoverProbability:
            # no crossover, just copy first parent
            return self.copy(self, False)

        # new chromosome object, copy chromosome setup
        n = self.copy(self, True)
        n_classes = n._classes
        n_slots = n._slots

        # number of classes
        size = len(self._classes)

        cp = size * [False]

        # determine crossover point (randomly)
        for i in range(numberOfCrossoverPoints, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(32768) % size
                if not cp[p]:
                    cp[p] = check_point = True

        # make new code by combining parent codes
        first = randrange(2) == 0
        classes = self._classes
        course_classes = list(classes.keys())
        parent_classes = parent2.classes
        parent_course_classes = list(parent2.classes.keys())
        for i in range(0, size):
            if first:
                course_class = course_classes[i]
                dur = course_class.Duration
                reservation = classes[course_class]
                reservation_index = reservation.index
                # insert class from first parent into new chromosome's class table
                n_classes[course_class] = reservation
                # all time-space slots of class are copied
                for slot in n_slots[reservation_index: reservation_index + dur]:
                    slot.append(course_class)
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation = parent_classes[course_class]
                reservation_index = reservation.index
                # insert class from second parent into new chromosome's class table
                n_classes[course_class] = reservation
                # all time-space slots of class are copied
                for slot in n_slots[reservation_index: reservation_index + dur]:
                    slot.append(course_class)

            # crossover point
            if cp[i]:
                # change source chromosome
                first = not first

        n.calculateFitness()

        # return smart pointer to offspring
        return n

    # Performs mutation on chromosome
    def mutation(self, mutationSize, mutationProbability):
        # check probability of mutation operation
        if randrange(32768) % 100 > mutationProbability:
            return

        classes = self._classes
        # number of classes
        numberOfClasses = len(classes)
        course_classes = list(classes.keys())
        configuration = self._configuration
        slots = self._slots
        nr = configuration.numberOfRooms

        DAY_HOURS = Constant.Constant.DAY_HOURS
        DAYS_NUM = Constant.Constant.DAYS_NUM

        # move selected number of classes at random position
        for i in range(mutationSize, 0, -1):
            # select ranom chromosome for movement
            mpos = randrange(32768) % numberOfClasses

            # current time-space slot used by class
            cc1 = course_classes[mpos]
            reservation1 = classes[cc1]

            # determine position of class randomly
            dur = cc1.Duration
            day = randrange(32768) % DAYS_NUM
            room = randrange(32768) % nr
            time = randrange(32768) % (DAY_HOURS + 1 - dur)
            reservation2 = Reservation.Reservation(nr, day, time, room)

            # move all time-space slots
            for j in range(0, dur):
                # remove class hour from current time-space slot
                cl = slots[reservation1.index + j]
                for cc1 in cl:
                    cl.remove(cc1)

                # move class hour to new time-space slot
                slots[reservation2.index + j].append(cc1)

            # change entry of class table to point to new time-space slots
            classes[cc1] = reservation2

        self.calculateFitness()

    # Calculates fitness value of chromosome
    def calculateFitness(self):
        # chromosome's score
        score = 0

        criteria = self._criteria
        configuration = self._configuration
        items = self._classes.items()
        slots = self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS = Constant.Constant.DAY_HOURS
        DAYS_NUM = Constant.Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        ci = 0

        # check criteria and calculate scores for each class in schedule
        for cc, reservation in items:
            # coordinate of time-space slot
            day = reservation.Day
            time = reservation.Time
            room = reservation.Room

            dur = cc.Duration

            # check for room overlapping of classes
            cls = slots[reservation.index: reservation.index + dur]
            ro = any(filter(lambda slot: len(slot) > 1, cls))

            # on room overlapping
            score = 0 if ro else score + 1

            criteria[ci + 0] = not ro

            r = configuration.getRoomById(room)
            # does current room have enough seats
            criteria[ci + 1] = r.NumberOfSeats >= cc.NumberOfSeats
            score = score + 1 if criteria[ci + 1] else score / 2

            # does current room have computers if they are required
            criteria[ci + 2] = (not cc.LabRequired) or (cc.LabRequired and r.Lab)
            score = score + 1 if criteria[ci + 2] else score / 2

            po = go = False

            # check overlapping of classes for professors and student groups
            t = day * daySize + time
            professorOverlaps = cc.professorOverlaps
            groupsOverlap = cc.groupsOverlap
            try:
                for k in range(numberOfRooms, 0, -1):
                    # for each hour of class
                    cl = slots[t: t + dur]
                    for cc1 in cl:
                        if cc != cc1:
                            # professor overlaps?
                            if not po and professorOverlaps(cc1):
                                po = True
                            # student group overlaps?
                            if not go and groupsOverlap(cc1):
                                go = True
                            # both type of overlapping? no need to check more
                            if po and go:
                                raise Exception('no need to check more')

                    t += DAY_HOURS
            except Exception:
                pass

            # professors have no overlapping classes?
            score = 0 if po else score + 1

            criteria[ci + 3] = not po

            # student groups has no overlapping classes?
            score = 0 if go else score + 1

            criteria[ci + 4] = not go
            ci += DAYS_NUM

        # calculate fitness value based on score
        self._fitness = score / (configuration.numberOfCourseClasses * DAYS_NUM)

    # Returns fitness value of chromosome
    @property
    def fitness(self):
        return self._fitness

    @property
    def configuration(self):
        return self._configuration

    @property
    # Returns reference to table of classes
    def classes(self):
        return self._classes

    @property
    # Returns array of flags of class requirements satisfaction
    def criteria(self):
        return self._criteria

    @property
    # Return reference to array of time-space slots
    def slots(self):
        return self._slots
