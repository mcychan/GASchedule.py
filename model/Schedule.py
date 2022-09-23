from .Constant import Constant
from .CourseClass import CourseClass
from .Reservation import Reservation
from .Criteria import Criteria
from collections import defaultdict, deque
from random import randrange

import numpy as np

# Schedule chromosome
class Schedule:
    # Initializes chromosomes with configuration block (setup of chromosome)
    def __init__(self, configuration):
        self._configuration = configuration
        # Fitness value of chromosome        
        self._fitness = 0

        # Time-space slots, one entry represent one hour in one classroom
        slots_length = Constant.DAYS_NUM * Constant.DAY_HOURS * self._configuration.numberOfRooms
        self._slots = [[] for _ in range(slots_length)]

        # Class table for chromosome
        # Used to determine first time-space slot used by class
        self._classes = defaultdict(Reservation)

        # Flags of class requirements satisfaction
        self._criteria = np.zeros(self._configuration.numberOfCourseClasses * Constant.CRITERIA_NUM, dtype=bool)
        
        self._diversity = 0.0
        self._rank = 0

    def copy(self, c, setup_only):
        if not setup_only:
            self._configuration = c.configuration
            # copy code
            self._slots, self._classes = c.slots[:], dict(c.classes)

            # copy flags of class requirements
            self._criteria = c.criteria[:]

            # copy fitness
            self._fitness = c.fitness
            return self

        return Schedule(c.configuration)

    # Makes new chromosome with same setup but with randomly chosen code
    def makeNewFromPrototype(self, positions = None):
        # make new chromosome, copy chromosome setup
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes

        # place classes at random position
        classes = self._configuration.courseClasses
        nr = self._configuration.numberOfRooms
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS
        for c in classes:
            # determine random position of class
            dur = c.Duration
            day = randrange(DAYS_NUM)
            room = randrange(nr)
            time = randrange(DAY_HOURS - dur)
            reservation = Reservation(nr, day, time, room)
            if positions is not None:
                positions.append(day)
                positions.append(room)
                positions.append(time)
            reservation_index = hash(reservation)

            # fill time-space slots, for each hour of class
            for i in range(reservation_index, reservation_index + dur):
                new_chromosome_slots[i].append(c)

            # insert in class table of chromosome
            new_chromosome_classes[c] = reservation

        new_chromosome.calculateFitness()
        return new_chromosome

    # Performs crossover operation using to chromosomes and returns pointer to offspring
    def crossover(self, parent, numberOfCrossoverPoints, crossoverProbability):
        # check probability of crossover operation
        if randrange(100) > crossoverProbability:
            # no crossover, just copy first parent
            return self.copy(self, False)

        # new chromosome object, copy chromosome setup
        n = self.copy(self, True)
        n_classes, n_slots = n._classes, n._slots

        classes = self._classes
        course_classes = tuple(classes.keys())
        parent_classes = parent.classes
        parent_course_classes = tuple(parent.classes.keys())

        # number of classes
        size = len(classes)

        cp = size * [False]

        # determine crossover point (randomly)
        for i in range(numberOfCrossoverPoints, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(size)
                if not cp[p]:
                    cp[p] = check_point = True

        # make new code by combining parent codes
        first = randrange(2) == 0
        
        for i in range(size):
            if first:
                course_class = course_classes[i]
                dur = course_class.Duration
                reservation = classes[course_class]
                reservation_index = hash(reservation)
                # insert class from first parent into new chromosome's class table
                n_classes[course_class] = reservation
                # all time-space slots of class are copied
                for j in range(reservation_index, reservation_index + dur):
                    n_slots[j].append(course_class)
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation = parent_classes[course_class]
                reservation_index = hash(reservation)
                # insert class from second parent into new chromosome's class table
                n_classes[course_class] = reservation
                # all time-space slots of class are copied
                for j in range(reservation_index, reservation_index + dur):
                    n_slots[j].append(course_class)

            # crossover point
            if cp[i]:
                # change source chromosome
                first = not first

        n.calculateFitness()

        # return smart pointer to offspring
        return n
        
    # Performs crossover operation using to chromosomes and returns pointer to offspring
    def crossovers(self, parent, r1, r2, r3, etaCross, crossoverProbability):
        # number of classes
        size = len(self._classes)
        jrand = randrange(size)
        
        nr = self._configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM

        # make new chromosome, copy chromosome setup
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes
        classes = self._classes
        course_classes = tuple(classes.keys())
        parent_classes = parent.classes
        parent_course_classes = tuple(parent.classes.keys())
        for i in range(size):
            if randrange(100) > crossoverProbability or i == jrand:
                course_class = course_classes[i]
                reservation1, reservation2, reservation3 = r1.classes[course_class], r2.classes[course_class], r3.classes[course_class]
                
                dur = course_class.Duration
                day = int(reservation3.Day + etaCross * (reservation1.Day - reservation2.Day))
                if day < 0:
                    day = 0
                elif day >= DAYS_NUM:
                    day = DAYS_NUM - 1
                    
                room = int(reservation3.Room + etaCross * (reservation1.Room - reservation2.Room))
                if room < 0:
                    room = 0
                elif room >= nr:
                    room = nr - 1
                    
                time = int(reservation3.Time + etaCross * (reservation1.Time - reservation2.Time))
                if time < 0:
                    time = 0
                elif time >= (DAY_HOURS - dur):
                    time = DAY_HOURS - 1 - dur
                    
                reservation = Reservation(nr, day, time, room)
                reservation_index = hash(reservation)

                # fill time-space slots, for each hour of class
                for j in range(reservation_index, reservation_index + dur):
                    new_chromosome_slots[j].append(course_class)

                # insert in class table of chromosome
                new_chromosome_classes[course_class] = reservation
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation = parent_classes[course_class]
                reservation_index = hash(reservation)
                
                # all time-space slots of class are copied
                for j in range(reservation_index, reservation_index + dur):
                    new_chromosome_slots[j].append(course_class)
                
                # insert class from second parent into new chromosome's class table
                new_chromosome_classes[course_class] = reservation
                
        new_chromosome.calculateFitness()

        # return smart pointer to offspring
        return new_chromosome

    def repair(self, cc1: CourseClass, reservation1: Reservation, reservation2: Reservation):
        nr = self._configuration.numberOfRooms
        slots = self._slots	
        reservation1_index, reservation2_index = hash(reservation1), hash(reservation2)
        dur = cc1.Duration

        if (reservation2_index + dur) >= len(slots):
            day = randrange(Constant.DAYS_NUM)
            room = randrange(nr)
            time = randrange(Constant.DAY_HOURS - dur)
            reservation2 = Reservation(nr, day, time, room)
            reservation2_index = hash(reservation2)

        # move all time-space slots
        for j in range(dur):
            # remove class hour from current time-space slot
            cl = slots[reservation1_index + j]
            clTuple = tuple(cl)
            for cc1 in clTuple:
                cl.remove(cc1)

            # move class hour to new time-space slot
            slots[reservation2_index + j].append(cc1)

        # change entry of class table to point to new time-space slots
        self._classes[cc1] = reservation2

    # Performs mutation on chromosome
    def mutation(self, mutationSize, mutationProbability):
        # check probability of mutation operation
        if randrange(100) > mutationProbability:
            return

        classes = self._classes
        # number of classes
        numberOfClasses = len(classes)
        course_classes = tuple(classes.keys())
        configuration = self._configuration
        nr = configuration.numberOfRooms

        DAY_HOURS = Constant.DAY_HOURS
        DAYS_NUM = Constant.DAYS_NUM

        # move selected number of classes at random position
        for i in range(mutationSize, 0, -1):
            # select ranom chromosome for movement
            mpos = randrange(numberOfClasses)

            # current time-space slot used by class
            cc1 = course_classes[mpos]
            reservation1 = classes[cc1]

            # determine position of class randomly
            dur = cc1.Duration
            day = randrange(DAYS_NUM)
            room = randrange(nr)
            time = randrange(DAY_HOURS - dur)
            reservation2 = Reservation(nr, day, time, room)
            self.repair(cc1, reservation1, reservation2)

        self.calculateFitness()

    # Calculates fitness value of chromosome
    def calculateFitness(self):
        # chromosome's score
        score = 0

        criteria, configuration = self._criteria, self._configuration
        items, slots = self._classes.items(), self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        ci = 0
        getRoomById = configuration.getRoomById

        # check criteria and calculate scores for each class in schedule
        for cc, reservation in items:
            # coordinate of time-space slot
            day, time, room = reservation.Day, reservation.Time, reservation.Room

            dur = cc.Duration

            ro = Criteria.isRoomOverlapped(slots, reservation, dur)

            # on room overlapping
            score = 0 if ro else score + 1

            criteria[ci + 0] = not ro

            r = getRoomById(room)
            # does current room have enough seats
            criteria[ci + 1] = Criteria.isSeatEnough(r, cc)
            score = score + 1 if criteria[ci + 1] else score / 2

            # does current room have computers if they are required
            criteria[ci + 2] = Criteria.isComputerEnough(r, cc)
            score = score + 1 if criteria[ci + 2] else score / 2

            po = go = False

            # check overlapping of classes for professors and student groups
            timeId = day * daySize + time
            po, go = Criteria.isOverlappedProfStudentGrp(slots, cc, numberOfRooms, timeId, dur)

            # professors have no overlapping classes?
            score = 0 if po else score + 1

            criteria[ci + 3] = not po

            # student groups has no overlapping classes?
            score = 0 if go else score + 1

            criteria[ci + 4] = not go
            ci += Constant.CRITERIA_NUM

        # calculate fitness value based on score
        self._fitness = score / (configuration.numberOfCourseClasses * DAYS_NUM)

    def getDifference(self, other):
        return np.logical_xor(self._criteria, other.criteria).sum()


    def extractPositions(self, positions):
        i = 0
        items = self._classes.items()
        for cc, reservation in items:
            positions[i] = reservation.Day
            i += 1
            positions[i] = reservation.Time
            i += 1
            positions[i] = reservation.Room
            i += 1


    def updatePositions(self, positions):
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS
        nr = self._configuration.numberOfRooms
        i = 0
        items = self._classes.items()
        for cc, reservation1 in items:
            dur = cc.Duration
            day = int(abs(positions[i] % DAYS_NUM))
            i += 1
            room = int(abs(positions[i] % nr))
            i += 1
            time = int(abs(positions[i] % (DAY_HOURS - dur)))
            i += 1

            reservation2 = Reservation(nr, day, time, room)
            self.repair(cc, reservation1, reservation2)

        self.calculateFitness()


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
        
    @property
    def diversity(self):
        return self._diversity

    @diversity.setter
    def diversity(self, new_diversity):
        self._diversity = new_diversity
        
    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, new_rank):
        self._rank = new_rank
