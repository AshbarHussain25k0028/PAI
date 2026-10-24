"""Courses, their study materials and their enrolled students.

Owner: Muhammad Mudassir (Part 2)
Lab concepts: Lab 03 (list vs set), Lab 05 (classes, constructors).

Key data structures
-------------------
- Course.materials : list[Material]  -> keeps the order the teacher added them.
- Course.enrolled  : set[str]        -> student IDs; a set stops duplicates and
                                        answers "is S01 enrolled?" in O(1).

INTERFACE STUB (Part 1): bodies are written in Part 2.
"""

from __future__ import annotations


class Material:
    """One piece of study material (a notes file) inside a course.

    Attributes:
        material_id (str), course_id (str), title (str),
        topic (str)      -> used by revision suggestions, e.g. "functions"
        file_name (str)  -> name of a .txt file in data/raw/notes/
    """

    def __init__(self, material_id: str, course_id: str, title: str,
                 topic: str, file_name: str):
        """Store the material's details.

        Args:
            material_id: e.g. "M01".
            course_id: the course it belongs to, e.g. "C101".
            title: name shown in the menu.
            topic: topic tag such as "oop".
            file_name: notes file inside data/raw/notes/.
        Raises:
            ValidationError: if an ID or the title is empty.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")

    def to_dict(self) -> dict:
        """Return the material as a plain dict (one CSV row).

        Returns:
            dict with the keys of materials.csv.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")

    @classmethod
    def from_dict(cls, row: dict) -> "Material":
        """Build a Material from one CSV row.

        Args:
            row: dict with material_id, course_id, title, topic, file_name.
        Returns:
            a new Material.
        Raises:
            ValidationError: if a column is missing or empty.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")


class Course:
    """A course taught by one teacher.

    Attributes:
        course_id (str), title (str), teacher_id (str)
        materials (list[Material])
        enrolled (set[str])
    """

    def __init__(self, course_id: str, title: str, teacher_id: str):
        """Create a course with no materials and no students yet.

        Args:
            course_id: e.g. "C101".
            title: e.g. "Programming for AI".
            teacher_id: the teacher who runs it, e.g. "T01".
        Raises:
            ValidationError: if any value is empty.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")

    def enroll(self, student_id: str) -> bool:
        """Add a student to the enrolled set.

        Args:
            student_id: e.g. "S03".
        Returns:
            True if added, False if they were already enrolled.
        Complexity: O(1) because of the set.
        """
        raise NotImplementedError("Part 2")

    def unenroll(self, student_id: str) -> None:
        """Remove a student from the course.

        Args:
            student_id: the student to remove.
        Raises:
            NotFoundError: if the student is not enrolled.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")

    def is_enrolled(self, student_id: str) -> bool:
        """Check whether a student is in this course.

        Args:
            student_id: the student to check.
        Returns:
            True if enrolled.
        Complexity: O(1) because of the set.
        """
        raise NotImplementedError("Part 2")

    def add_material(self, material: Material) -> None:
        """Append a material to the end of the list.

        Args:
            material: the Material to add.
        Raises:
            DuplicateError: if a material with the same ID exists.
        Complexity: O(m) for m materials (the duplicate check).
        """
        raise NotImplementedError("Part 2")

    def materials_for_topic(self, topic: str) -> list[Material]:
        """All materials whose topic matches (case-insensitive).

        Args:
            topic: e.g. "files".
        Returns:
            list of matching Material objects, in display order.
        Complexity: O(m) for m materials.
        """
        raise NotImplementedError("Part 2")

    def to_dict(self) -> dict:
        """Return id, title and teacher as a plain dict (one CSV row).

        Returns:
            {"course_id", "title", "teacher_id"}.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")

    @classmethod
    def from_dict(cls, row: dict) -> "Course":
        """Build a Course from one CSV row.

        Args:
            row: dict with course_id, title, teacher_id.
        Returns:
            a new Course (no materials or students yet).
        Raises:
            ValidationError: if a column is missing or empty.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 2")
