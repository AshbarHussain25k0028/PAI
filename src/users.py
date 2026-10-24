"""User accounts: an abstract User and three roles.

Owner: Ashbar Hussain (Part 3)
Lab concepts: Lab 05 (abstract base class, inheritance, method overriding,
polymorphism, encapsulation).

How the roles work
------------------
User is an abstract base class (ABC): you cannot create a plain User.
Student, Teacher and Admin each override menu_options() and can_view_student().
The menu code calls user.menu_options() without checking the role; this is
polymorphism.

Key data structure: all users live in a dict {user_id: User}, so login and
lookups are O(1).

INTERFACE STUB (Part 1): bodies are written in Part 3.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class User(ABC):
    """Shared account details for every role.

    Attributes (read-only properties):
        user_id (str), name (str), role (str)
    """

    def __init__(self, user_id: str, name: str):
        """Store the ID and name in protected attributes (_user_id, _name).

        Args:
            user_id: e.g. "S01", "T01" or "A01".
            name: the person's display name.
        Raises:
            ValidationError: if the ID or name is empty.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    @property
    @abstractmethod
    def role(self) -> str:
        """The role name of this account.

        Returns:
            "student", "teacher" or "admin".
        Complexity: O(1).
        """

    @abstractmethod
    def menu_options(self) -> list[str]:
        """Menu lines this role may see.

        Returns:
            list of menu lines, in display order.
        Complexity: O(1).
        """

    @abstractmethod
    def can_view_student(self, student_id: str, courses: dict) -> bool:
        """May this user see the given student's records?

        Args:
            student_id: the student whose work is requested.
            courses: {course_id: Course}, used by Teacher to check enrollment.
        Returns:
            True if allowed.
        Complexity: Student/Admin O(1); Teacher O(c) for c courses.
        """

    def describe(self) -> str:
        """One-line summary of the account.

        Returns:
            text such as "S01 - Ali Raza (student)".
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def to_dict(self) -> dict:
        """The account as a plain dict for saving to JSON.

        Returns:
            {"user_id", "name", "role"}.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")


class Student(User):
    """A student: sees only their own work."""

    @property
    def role(self) -> str:
        """The role name.

        Returns:
            "student".
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def menu_options(self) -> list[str]:
        """Menu lines for a student.

        Returns:
            list of menu lines (my courses, quizzes, assignments, progress).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def can_view_student(self, student_id: str, courses: dict) -> bool:
        """A student may only see their own records.

        Args:
            student_id: the student whose work is requested.
            courses: not needed here; kept so every role has the same call.
        Returns:
            True only if student_id is their own ID.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")


class Teacher(User):
    """A teacher: sees students enrolled in the courses they teach."""

    @property
    def role(self) -> str:
        """The role name.

        Returns:
            "teacher".
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def menu_options(self) -> list[str]:
        """Menu lines for a teacher.

        Returns:
            list of menu lines (materials, quizzes, marking, class report).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def can_view_student(self, student_id: str, courses: dict) -> bool:
        """A teacher may see students enrolled in a course they teach.

        Args:
            student_id: the student whose work is requested.
            courses: {course_id: Course}.
        Returns:
            True if the student is in one of this teacher's courses.
        Complexity: O(c) for c courses (set lookup inside each course).
        """
        raise NotImplementedError("Part 3")


class Admin(User):
    """An administrator: manages accounts and enrollment, sees everyone."""

    @property
    def role(self) -> str:
        """The role name.

        Returns:
            "admin".
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def menu_options(self) -> list[str]:
        """Menu lines for an admin.

        Returns:
            list of menu lines (accounts, enrollment, save).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")

    def can_view_student(self, student_id: str, courses: dict) -> bool:
        """An admin may see every student.

        Args:
            student_id: the student whose work is requested.
            courses: not needed here; kept so every role has the same call.
        Returns:
            always True.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 3")


def user_from_dict(record: dict) -> User:
    """Create the right subclass from a saved record.

    Uses a dict {"student": Student, "teacher": Teacher, "admin": Admin}.

    Args:
        record: {"user_id", "name", "role"} from users.json.
    Returns:
        a Student, Teacher or Admin object.
    Raises:
        ValidationError: unknown role or missing field.
    Complexity: O(1).
    """
    raise NotImplementedError("Part 3")


def find_user(users: dict, user_id: str) -> User:
    """Return users[user_id] (ID is matched case-insensitively).

    Args:
        users: {user_id: User}.
        user_id: the ID typed at login, e.g. "s01".
    Returns:
        the matching User.
    Raises:
        NotFoundError: if there is no such user.
    Complexity: O(1).
    """
    raise NotImplementedError("Part 3")
