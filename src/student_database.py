# Write your solution here
def add_student(database: dict, student: str):

    pass


def print_student(database: dict, student: str):
   pass

def add_course(database: dict, student: str, course: tuple):


    pass


def summary(database: dict):
    pass


def main():
    students = {}
    add_student(students, "Peter")
    add_student(students, "Emily")

    add_course(students, "Peter", ("Introduction to Programming", 5))
    add_course(students, "Peter", ("Data Structures and Algorithms", 3))
    add_course(students, "Emily", ("Introduction to Programming", 4))
    add_course(students, "Emily", ("Introduction to Programming", 5))  # retake, keeps the higher grade

    print_student(students, "Peter")
    print_student(students, "Emily")
    print_student(students, "Nobody")  # not in the database

    summary(students)


if __name__ == "__main__":
    main()
