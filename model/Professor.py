# Stores data about professor
class Professor:
    # Initializes professor data
    def __init__(self, id, name):
        self.Id = id
        self.Name = name
        self.CourseClasses = []

    # Bind professor to course
    def addCourseClass(self, courseClass):
        self.CourseClasses.append(courseClass)
        
    # Compares ID's of two objects which represent professors
    def __eq__(self, rhs):
        return self.Id == rhs.Id
