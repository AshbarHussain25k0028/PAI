"""Account and enrollment management for the admin menu.

Owner: Ashbar Hussain (Part 8)
Lab concepts: Lab 03 (dict lookups, set membership), Lab 05 (polymorphism:
the right User subclass is picked from a dict), Lab 06 (custom exceptions).

These functions only change the data in memory and never ask for input, so
the menu code in main.py stays short and the logic can be checked on its own.
Saving to disk happens in DataStore.save() (Part 5).

Key data structures
-------------------
- users       : dict {user_id: User}, so "does this ID exist?" is O(1).
- ROLE_PREFIX : dict {role: ID prefix}, e.g. "student" -> "S".
- Course.enrolled : set of student IDs, so enrolling twice is caught in O(1).
"""

from __future__ import annotations

from exceptions import DuplicateError, NotFoundError, ValidationError
from users import ROLE_CLASSES
from utils import make_id, require_text

# The first letter(s) of every new ID, per role: S01, T01, A01 ...
ROLE_PREFIX = {"student": "S", "teacher": "T", "admin": "A"}


def create_account(users: dict, role: str, name: str):
    """Make a new account with the next free ID and add it to users.

    Args:
        users: {user_id: User}; the new user is added to it.
        role: "student", "teacher" or "admin" (any case).
        name: the person's display name.
    Returns:
        the new Student, Teacher or Admin object.
    Raises:
        ValidationError: unknown role or empty name.
    Complexity: O(u) for u users (make_id scans the IDs once).
    """
    role = require_text(role, "role").lower()
    if role not in ROLE_CLASSES:
        raise ValidationError(f"Unknown role '{role}'.")
    new_id = make_id(ROLE_PREFIX[role], users.keys())
    user = ROLE_CLASSES[role](new_id, require_text(name, "name"))
    users[user.user_id] = user
    return user


def enroll_student(users: dict, courses: dict, student_id: str,
                   course_id: str) -> None:
    """Add a student to a course's enrolled set.

    Args:
        users: {user_id: User}.
        courses: {course_id: Course}.
        student_id: e.g. "S03" (any case).
        course_id: e.g. "C102" (any case).
    Raises:
        NotFoundError: no such user or course.
        ValidationError: the user is not a student.
        DuplicateError: the student is already enrolled.
    Complexity: O(1) (dict lookups and a set add).
    """
    student_id = str(student_id).strip().upper()
    course_id = str(course_id).strip().upper()
    if student_id not in users:
        raise NotFoundError(f"No user with ID '{student_id}'.")
    if users[student_id].role != "student":
        raise ValidationError(f"{student_id} is not a student account.")
    if course_id not in courses:
        raise NotFoundError(f"No course with ID '{course_id}'.")
    if not courses[course_id].enroll(student_id):
        raise DuplicateError(f"{student_id} is already enrolled in {course_id}.")


def accounts_by_role(users: dict) -> list:
    """All accounts in a fixed order: admins, teachers, students, then by ID.

    Args:
        users: {user_id: User}.
    Returns:
        list of User objects.
    Complexity: O(u log u) for u users.
    """
    order = {"admin": 0, "teacher": 1, "student": 2}
    return sorted(users.values(),
                  key=lambda user: (order.get(user.role, 3), user.user_id))


def students_not_in(users: dict, course) -> list:
    """Students who could still be enrolled in a course.

    Args:
        users: {user_id: User}.
        course: the Course.
    Returns:
        list of Student objects not in course.enrolled, sorted by ID.
    Complexity: O(u log u) for u users (set lookup per user).
    """
    return sorted((user for user in users.values()
                   if user.role == "student"
                   and not course.is_enrolled(user.user_id)),
                  key=lambda user: user.user_id)
