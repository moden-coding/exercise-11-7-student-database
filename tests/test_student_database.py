#!/usr/bin/env python3
import contextlib
import io
import unittest

from src.student_database import add_course, add_student, print_student, summary


def run_and_capture(func, *args):
    """Call func(*args) and return its printed output as a list of lines."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args)
    return [line for line in buf.getvalue().split("\n") if line]


class TestPrintStudent(unittest.TestCase):
    """print_student(students, name) -> prints a student's course summary."""

    def test_functions_are_callable(self):
        try:
            students = {}
            add_student(students, "Peter")
            print_student(students, "Peter")
        except Exception as e:
            self.fail(
                "add_student(students, name) and print_student(students, name) "
                "should be callable as in:\nstudents = {}\n"
                'add_student(students, "Peter")\n'
                'print_student(students, "Peter")\nGot exception: %r' % (e,)
            )

    def test_student_with_no_completed_courses(self):
        students = {}
        add_student(students, "Peter")
        output = run_and_capture(print_student, students, "Peter")
        expected = ["Peter:", " no completed courses"]
        self.assertEqual(
            output, expected,
            msg="print_student(students, 'Peter') for a student with no "
            "completed courses should print:\n%s\nGot:\n%s" % (expected, output),
        )

    def test_student_not_in_database(self):
        students = {}
        add_student(students, "Peter")
        output = run_and_capture(print_student, students, "Emily")
        expected = ["Emily: no such person in the database"]
        self.assertEqual(
            output, expected,
            msg="print_student(students, 'Emily') when 'Emily' was never "
            "added should print '%s'. Got: %s" % (expected[0], output),
        )

    def test_multiple_students_including_one_not_added(self):
        students = {}
        add_student(students, "Peter")
        add_student(students, "Emily")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_student(students, "Peter")
            print_student(students, "Emily")
            print_student(students, "Andy")
        output = [line for line in buf.getvalue().split("\n") if line]
        expected = [
            "Peter:", " no completed courses",
            "Emily:", " no completed courses",
            "Andy: no such person in the database",
        ]
        self.assertEqual(
            output, expected,
            msg="Printing Peter, Emily (both added, no courses) then Andy "
            "(never added) should print:\n%s\nGot:\n%s" % (expected, output),
        )


class TestAddCourse(unittest.TestCase):
    """add_course(students, name, (course, grade)) -> records a completed course."""

    def test_function_is_callable(self):
        try:
            students = {}
            add_student(students, "Peter")
            add_course(students, "Peter", ("Introduction to Programming", 5))
        except Exception as e:
            self.fail(
                "add_course(students, name, (course, grade)) should be "
                "callable as in:\nstudents = {}\n"
                'add_student(students, "Peter")\n'
                'add_course(students, "Peter", '
                '("Introduction to Programming", 5))\nGot exception: %r' % (e,)
            )

    def test_completion_is_printed_out(self):
        students = {}
        add_student(students, "Peter")
        add_course(students, "Peter", ("Introduction to Programming", 5))
        output = run_and_capture(print_student, students, "Peter")
        expected = [
            "Peter:", " 1 completed courses:",
            "  Introduction to Programming 5", " average grade 5.0",
        ]
        self.assertEqual(
            output, expected,
            msg="After adding one course with grade 5, print_student should "
            "print:\n%s\nGot:\n%s" % (expected, output),
        )

    def test_multiple_completions_both_listed(self):
        students = {}
        add_student(students, "Peter")
        add_course(students, "Peter", ("Introduction to Programming", 5))
        add_course(students, "Peter", ("Data Structures and Algorithms", 3))
        output = run_and_capture(print_student, students, "Peter")
        expected1 = [
            "Peter:", " 2 completed courses:",
            "  Introduction to Programming 5",
            "  Data Structures and Algorithms 3",
            " average grade 4.0",
        ]
        expected2 = [
            "Peter:", " 2 completed courses:",
            "  Data Structures and Algorithms 3",
            "  Introduction to Programming 5",
            " average grade 4.0",
        ]
        self.assertTrue(
            output == expected1 or output == expected2,
            msg="After adding two courses (grades 5 and 3), print_student "
            "should print both courses (order doesn't matter) and average "
            "grade 4.0. Expected one of:\n%s\nor\n%s\nGot:\n%s"
            % (expected1, expected2, output),
        )

    def test_completions_for_multiple_students(self):
        students = {}
        add_student(students, "Emily")
        add_student(students, "Peter")
        add_course(students, "Emily", ("Introduction to Programming", 5))
        add_course(students, "Emily", ("Introduction to Databases", 4))
        add_course(students, "Peter", ("Data Structures and Algorithms", 3))
        output = run_and_capture(print_student, students, "Emily")
        expected1 = [
            "Emily:", " 2 completed courses:",
            "  Introduction to Programming 5",
            "  Introduction to Databases 4",
            " average grade 4.5",
        ]
        expected2 = [
            "Emily:", " 2 completed courses:",
            "  Introduction to Databases 4",
            "  Introduction to Programming 5",
            " average grade 4.5",
        ]
        self.assertTrue(
            output == expected1 or output == expected2,
            msg="Emily's courses should print independently of Peter's. "
            "Expected one of:\n%s\nor\n%s\nGot:\n%s"
            % (expected1, expected2, output),
        )

    def test_fail_grade_is_not_registered(self):
        students = {}
        add_student(students, "Peter")
        add_course(students, "Peter", ("Software Development Methods", 0))
        output = run_and_capture(print_student, students, "Peter")
        expected = ["Peter:", " no completed courses"]
        self.assertEqual(
            output, expected,
            msg="A course completed with grade 0 (fail) should not count "
            "as completed. Expected:\n%s\nGot:\n%s" % (expected, output),
        )

    def test_lower_grade_on_retake_is_ignored(self):
        students = {}
        add_student(students, "Peter")
        add_course(students, "Peter", ("Software Development Methods", 5))
        add_course(students, "Peter", ("Software Development Methods", 1))
        output = run_and_capture(print_student, students, "Peter")
        expected = [
            "Peter:", " 1 completed courses:",
            "  Software Development Methods 5", " average grade 5.0",
        ]
        self.assertEqual(
            output, expected,
            msg="Retaking a course with a LOWER grade (5 then 1) should "
            "keep the higher grade (5), not overwrite it. Expected:\n%s\n"
            "Got:\n%s" % (expected, output),
        )

    def test_grade_can_be_raised_on_retake(self):
        students = {}
        add_student(students, "Peter")
        add_course(students, "Peter", ("Software Development Methods", 1))
        add_course(students, "Peter", ("Software Development Methods", 5))
        output = run_and_capture(print_student, students, "Peter")
        expected = [
            "Peter:", " 1 completed courses:",
            "  Software Development Methods 5", " average grade 5.0",
        ]
        self.assertEqual(
            output, expected,
            msg="Retaking a course with a HIGHER grade (1 then 5) should "
            "raise the recorded grade to 5. Expected:\n%s\nGot:\n%s"
            % (expected, output),
        )

    def test_multiple_students_multiple_courses(self):
        students = {}
        add_student(students, "Emily")
        add_student(students, "Peter")
        add_course(students, "Emily", ("Software Development Methods", 4))
        add_course(students, "Emily", ("Software Development Methods", 5))
        add_course(students, "Peter", ("Data Structures and Algorithms", 3))
        add_course(students, "Peter", ("Models of Computation", 0))
        add_course(students, "Peter", ("Data Structures and Algorithms", 2))
        add_course(students, "Peter", ("Introduction to Computer Science", 1))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_student(students, "Emily")
            print_student(students, "Peter")
        output = [line for line in buf.getvalue().split("\n") if line]
        expected1 = [
            "Emily:", " 1 completed courses:",
            "  Software Development Methods 5", " average grade 5.0",
            "Peter:", " 2 completed courses:",
            "  Data Structures and Algorithms 3",
            "  Introduction to Computer Science 1",
            " average grade 2.0",
        ]
        expected2 = [
            "Emily:", " 1 completed courses:",
            "  Software Development Methods 5", " average grade 5.0",
            "Peter:", " 2 completed courses:",
            "  Introduction to Computer Science 1",
            "  Data Structures and Algorithms 3",
            " average grade 2.0",
        ]
        self.assertTrue(
            output == expected1 or output == expected2,
            msg="Emily retook Software Development Methods (4 then 5, "
            "should keep 5) and Peter has a failed course (Models of "
            "Computation, grade 0, should not count) among his completions. "
            "Expected one of:\n%s\nor\n%s\nGot:\n%s"
            % (expected1, expected2, output),
        )


class TestSummary(unittest.TestCase):
    """summary(students) -> prints database-wide stats."""

    def test_function_is_callable(self):
        try:
            students = {}
            add_student(students, "Peter")
            add_course(students, "Peter", ("Software Development Methods", 5))
            summary(students)
        except Exception as e:
            self.fail(
                "summary(students) should be callable as in:\nstudents = {}\n"
                'add_student(students, "Peter")\n'
                'add_course(students, "Peter", '
                '("Software Development Methods", 5))\n'
                "summary(students)\nGot exception: %r" % (e,)
            )

    def test_single_student(self):
        students = {}
        add_student(students, "Peter")
        add_course(students, "Peter", ("Software Development Methods", 5))
        output = run_and_capture(summary, students)
        expected = [
            "students 1",
            "most courses completed 1 Peter",
            "best average grade 5.0 Peter",
        ]
        self.assertEqual(
            output, expected,
            msg="summary() with a single student (Peter, 1 course, grade 5) "
            "should print:\n%s\nGot:\n%s" % (expected, output),
        )

    def test_multiple_students(self):
        students = {}
        add_student(students, "Emily")
        add_student(students, "Peter")
        add_course(students, "Emily", ("Software Development Methods", 4))
        add_course(students, "Emily", ("Software Development Methods", 5))
        add_course(students, "Peter", ("Data Structures and Algorithms", 3))
        add_course(students, "Peter", ("Models of Computation", 0))
        add_course(students, "Peter", ("Data Structures and Algorithms", 2))
        add_course(students, "Peter", ("Introduction to Computer Science", 1))
        add_course(students, "Peter", ("Software Engineering", 3))
        output = run_and_capture(summary, students)
        expected = [
            "students 2",
            "most courses completed 3 Peter",
            "best average grade 5.0 Emily",
        ]
        self.assertEqual(
            output, expected,
            msg="summary() with two students (Peter has 3 completed courses, "
            "Emily has the best average grade of 5.0) should print:\n%s\n"
            "Got:\n%s" % (expected, output),
        )


if __name__ == "__main__":
    unittest.main()
