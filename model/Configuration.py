import codecs
import json

from .Professor import Professor
from .StudentsGroup import StudentsGroup
from .Course import Course
from .Room import Room
from .CourseClass import CourseClass


# Reads configuration file and stores parsed objects
class Configuration:

    # Initialize data
    def __init__(self):
        # Indicate that configuration is not parsed yet
        self._isEmpty = True
        # parsed professors
        self._professors = {}
        # parsed student groups
        self._studentGroups = {}
        # parsed courses
        self._courses = {}
        # parsed rooms
        self._rooms = {}
        # parsed classes
        self._courseClasses = []

    # Returns professor with specified ID
    # If there is no professor with such ID method returns NULL
    def getProfessorById(self, id) -> Professor:
        if id in self._professors:
            return self._professors[id]
        return None

    @property
    # Returns number of parsed professors
    def numberOfProfessors(self) -> int:
        return len(self._professors)

    # Returns student group with specified ID
    # If there is no student group with such ID method returns NULL
    def getStudentsGroupById(self, id) -> StudentsGroup:
        if id in self._studentGroups:
            return self._studentGroups[id]
        return None

    @property
    # Returns number of parsed student groups
    def numberOfStudentGroups(self) -> int:
        return len(self._studentGroups)

    # Returns course with specified ID
    # If there is no course with such ID method returns NULL
    def getCourseById(self, id) -> Course:
        if id in self._courses:
            return self._courses[id]
        return None

    @property
    def numberOfCourses(self) -> int:
        return len(self._courses)

    # Returns room with specified ID
    # If there is no room with such ID method returns NULL
    def getRoomById(self, id) -> Room:
        if id in self._rooms:
            return self._rooms[id]
        return None

    @property
    # Returns number of parsed rooms
    def numberOfRooms(self) -> int:
        return len(self._rooms)

    @property
    # Returns reference to list of parsed classes
    def courseClasses(self) -> []:
        return self._courseClasses

    @property
    # Returns number of parsed classes
    def numberOfCourseClasses(self) -> int:
        return len(self._courseClasses)

    @property
    # Returns TRUE if configuration is not parsed yet
    def isEmpty(self) -> bool:
        return self._isEmpty

    # Reads professor's data from config file, makes object and returns
    # Returns NULL if method cannot parse configuration data
    @staticmethod
    def __parseProfessor(dictConfig):
        id = 0
        name = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]

        if id == 0 or name == '':
            return None
        return Professor(id, name)

    # Reads StudentsGroup's data from config file, makes object and returns
    # Returns None if method cannot parse configuration data
    @staticmethod
    def __parseStudentsGroup(dictConfig):
        id = 0
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if id == 0:
            return None
        return StudentsGroup(id, name, size)

    # Reads course's data from config file, makes object and returns
    # Returns None if method dictConfig parse configuration data
    @staticmethod
    def __parseCourse(dictConfig):
        id = 0
        name = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]

        if id == 0:
            return None
        return Course(id, name)

    # Reads rooms's data from config file, makes object and returns
    # Returns None if method cannot parse configuration data
    @staticmethod
    def __parseRoom(dictConfig):
        lab = False
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'lab':
                lab = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if size == 0 or name == '':
            return None
        return Room(name, lab, size)

    # Reads class' data from config file, makes object and returns pointer
    # Returns None if method cannot parse configuration data
    def __parseCourseClass(self, dictConfig):
        pid = 0
        cid = 0
        dur = 1
        lab = False
        group_list = []

        for key in dictConfig:
            if key == 'professor':
                pid = dictConfig[key]
            elif key == 'course':
                cid = dictConfig[key]
            elif key == 'lab':
                lab = dictConfig[key]
            elif key == 'duration':
                dur = dictConfig[key]
            elif key == 'group' or key == 'groups':
                groups = dictConfig[key]
                if isinstance(groups, list):
                    for grp in groups:
                        g = self.getStudentsGroupById(grp)
                        if g:
                            group_list.append(g)
                else:
                    g = self.getStudentsGroupById(groups)
                    if g:
                        group_list.append(g)

        # get professor who teaches class and course to which this class belongs
        p = self.getProfessorById(pid)
        c = self.getCourseById(cid)

        # does professor and class exists
        if not c or not p:
            return None

        # make object and return
        return CourseClass(p, c, lab, dur, group_list)

    # parse file and store parsed object
    def parseFile(self, fileName):
        # clear previously parsed objects
        self._professors = {}
        self._studentGroups = {}
        self._courses = {}
        self._rooms = {}
        self._courseClasses = []

        Room.restartIDs()
        CourseClass.restartIDs()

        with codecs.open(fileName, "r", "utf-8") as f:
            # read file into a string and deserialize JSON to a type
            data = json.load(f)

        for dictConfig in data:
            for key in dictConfig:
                if key == 'prof':
                    prof = self.__parseProfessor(dictConfig[key])
                    self._professors[prof.Id] = prof
                elif key == 'course':
                    course = self.__parseCourse(dictConfig[key])
                    self._courses[course.Id] = course
                elif key == 'room':
                    room = self.__parseRoom(dictConfig[key])
                    self._rooms[room.Id] = room
                elif key == 'group':
                    group = self.__parseStudentsGroup(dictConfig[key])
                    self._studentGroups[group.Id] = group
                elif key == 'class':
                    courseClass = self.__parseCourseClass(dictConfig[key])
                    self._courseClasses.append(courseClass)

        self._isEmpty = False
