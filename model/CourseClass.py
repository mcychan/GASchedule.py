class CourseClass:
    # ID counter used to assign IDs automatically
    _next_class_id = 0

    # Initializes class object
    def __init__(self, professor, course, requires_lab, duration, groups):
        self.Id = CourseClass._next_class_id
        CourseClass._next_class_id += 1
        # Return pointer to professor who teaches
        self.Professor = professor
        # Return pointer to course to which class belongs
        self.Course = course
        # Returns number of seats (students) required in room
        self.NumberOfSeats = 0
        # Returns TRUE if class requires computers in room.
        self.LabRequired = requires_lab
        # Returns duration of class in hours
        self.Duration = duration
        # Returns reference to list of student groups who attend class
        self.Groups = set(groups)

        # bind professor to class
        self.Professor.addCourseClass(self)

        # bind student groups to class
        for grp in self.Groups:  # self.groups:
            grp.addClass(self)
            self.NumberOfSeats += grp.NumberOfStudents

    # Returns TRUE if another class has one or overlapping student groups.
    def groupsOverlap(self, c):
        return len(self.Groups & c.Groups) > 0

    # Returns TRUE if another class has same professor.
    def professorOverlaps(self, c):
        return self.Professor == c.Professor

    def __hash__(self):
        return hash(self.Id)

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
        CourseClass._next_class_id = 0
