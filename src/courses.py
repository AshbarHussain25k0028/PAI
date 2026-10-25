"""Courses, their study materials and their enrolled students.

Owner: Muhammad Mudassir (Part 2)
Lab concepts: Lab 03 (list vs set), Lab 05 (classes, constructors).

Key data structures
-------------------
- Course.materials : list[Material]  -> keeps the order the teacher added them.
- Course.enrolled  : set[str]        -> student IDs; a set stops duplicates and
                                        answers "is S01 enrolled?" in O(1).
"""

from __future__ import annotations

from exceptions import DuplicateError, NotFoundError, ValidationError
from utils import require_text

# Column order of materials.csv, used by to_dict / from_dict.
MATERIAL_FIELDS = ("material_id", "course_id", "title", "topic", "file_name")
# Column order of courses.csv.
COURSE_FIELDS = ("course_id", "title", "teacher_id")


def _read_row(row: dict, fields: tuple) -> dict:
    """Pick the given columns out of a CSV row and check none is empty.

    Args:
        row: one CSV row as a dict.
        fields: the column names that must be present.
    Returns:
        a new dict with only those columns, values stripped.
    Raises:
        ValidationError: if row is not a dict, or a column is missing or empty.
    Complexity: O(f) for f fields.
    """
    if not isinstance(row, dict):
        raise ValidationError("Each row must be a dict of column -> value.")
    return {field: require_text(row.get(field), field) for field in fields}


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
        self.material_id = require_text(material_id, "material_id")
        self.course_id = require_text(course_id, "course_id")
        self.title = require_text(title, "title")
        self.topic = require_text(topic, "topic").lower()
        self.file_name = require_text(file_name, "file_name")

    def __repr__(self) -> str:
        """Short text form, handy when printing in the console.

        Returns:
            e.g. "Material(M01, 'Writing functions', functions)".
        Complexity: O(1).
        """
        return f"Material({self.material_id}, {self.title!r}, {self.topic})"

    def to_dict(self) -> dict:
        """Return the material as a plain dict (one CSV row).

        Returns:
            dict with the keys of materials.csv.
        Complexity: O(1).
        """
        return {field: getattr(self, field) for field in MATERIAL_FIELDS}

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
        return cls(**_read_row(row, MATERIAL_FIELDS))


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
        self.course_id = require_text(course_id, "course_id")
        self.title = require_text(title, "title")
        self.teacher_id = require_text(teacher_id, "teacher_id")
        self.materials: list[Material] = []   # ordered, as the teacher added them
        self.enrolled: set[str] = set()       # student IDs, no duplicates

    def __repr__(self) -> str:
        """Short text form, handy when printing in the console.

        Returns:
            e.g. "Course(C101, 'Programming for AI', 8 students)".
        Complexity: O(1).
        """
        return (f"Course({self.course_id}, {self.title!r}, "
                f"{len(self.enrolled)} students)")

    def enroll(self, student_id: str) -> bool:
        """Add a student to the enrolled set.

        Args:
            student_id: e.g. "S03".
        Returns:
            True if added, False if they were already enrolled.
        Raises:
            ValidationError: if student_id is empty.
        Complexity: O(1) because of the set.
        """
        student_id = require_text(student_id, "student_id")
        if student_id in self.enrolled:
            return False
        self.enrolled.add(student_id)
        return True

    def unenroll(self, student_id: str) -> None:
        """Remove a student from the course.

        Args:
            student_id: the student to remove.
        Raises:
            NotFoundError: if the student is not enrolled.
        Complexity: O(1).
        """
        if student_id not in self.enrolled:
            raise NotFoundError(
                f"{student_id} is not enrolled in {self.course_id}.")
        self.enrolled.remove(student_id)

    def is_enrolled(self, student_id: str) -> bool:
        """Check whether a student is in this course.

        Args:
            student_id: the student to check.
        Returns:
            True if enrolled.
        Complexity: O(1) because of the set.
        """
        return student_id in self.enrolled

    def add_material(self, material: Material) -> None:
        """Append a material to the end of the list.

        Args:
            material: the Material to add.
        Raises:
            ValidationError: if it is not a Material or belongs to another course.
            DuplicateError: if a material with the same ID exists.
        Complexity: O(m) for m materials (the duplicate check).
        """
        if not isinstance(material, Material):
            raise ValidationError("Only Material objects can be added.")
        if material.course_id != self.course_id:
            raise ValidationError(
                f"{material.material_id} belongs to {material.course_id}, "
                f"not {self.course_id}.")
        if any(old.material_id == material.material_id
               for old in self.materials):
            raise DuplicateError(
                f"Material {material.material_id} is already in {self.course_id}.")
        self.materials.append(material)

    def materials_for_topic(self, topic: str) -> list[Material]:
        """All materials whose topic matches (case-insensitive).

        Args:
            topic: e.g. "files".
        Returns:
            list of matching Material objects, in display order.
        Complexity: O(m) for m materials.
        """
        wanted = topic.strip().lower()
        return [material for material in self.materials
                if material.topic == wanted]

    def to_dict(self) -> dict:
        """Return id, title and teacher as a plain dict (one CSV row).

        Returns:
            {"course_id", "title", "teacher_id"}.
        Complexity: O(1).
        """
        return {field: getattr(self, field) for field in COURSE_FIELDS}

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
        return cls(**_read_row(row, COURSE_FIELDS))
