"""Assignments, student submissions and protected marking.

Owner: Ashbar Hussain (Part 6)
Lab concepts: Lab 03 (tuple as a dict key), Lab 05 (encapsulation with
@property), datetime for deadlines.

Key data structures
-------------------
- Assignment.deadline : datetime.datetime, so "is it late?" is one comparison.
- submissions         : dict {(student_id, assignment_id): Submission}.
                        The tuple key means one submission per student per
                        assignment, found in O(1).
- Submission._marks   : None until marked; changed only through the marks
                        property, which rejects values below 0 or above max.

INTERFACE STUB (Part 1): bodies are written in Part 6.
"""

from __future__ import annotations


class Assignment:
    """A piece of coursework with a deadline.

    Attributes:
        assignment_id (str), course_id (str), title (str),
        deadline (datetime), max_marks (int)
    """

    def __init__(self, assignment_id: str, course_id: str, title: str,
                 deadline, max_marks: int):
        """Store the assignment details.

        Args:
            assignment_id: e.g. "AS01".
            course_id: the course it belongs to.
            title: name shown in the menu.
            deadline: datetime.datetime of the last allowed moment.
            max_marks: highest mark possible (> 0).
        Raises:
            ValidationError: empty values or max_marks <= 0.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    def is_open(self, now) -> bool:
        """Check whether the deadline has not passed yet.

        Args:
            now: datetime.datetime to compare with.
        Returns:
            True if now <= deadline.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    def to_dict(self) -> dict:
        """The assignment as a plain dict for JSON.

        Returns:
            dict with the keys of assignments.json (deadline as text).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    @classmethod
    def from_dict(cls, record: dict) -> "Assignment":
        """Build an Assignment from one JSON record.

        Args:
            record: dict with assignment_id, course_id, title, deadline,
                max_marks.
        Returns:
            a new Assignment.
        Raises:
            ValidationError: missing field, bad date or bad max_marks.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")


class Submission:
    """One student's work for one assignment.

    Attributes:
        student_id (str), assignment_id (str), submitted_at (datetime),
        text (str), marks (int | None, protected), feedback (str)
    """

    def __init__(self, student_id: str, assignment_id: str, submitted_at,
                 text: str, max_marks: int):
        """Create an unmarked submission.

        Args:
            student_id: who submitted.
            assignment_id: which assignment.
            submitted_at: datetime.datetime of submission.
            text: the answer text.
            max_marks: copied from the Assignment, used by the marks setter.
        Raises:
            ValidationError: if an ID is empty.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    @property
    def key(self) -> tuple:
        """The dict key of this submission.

        Returns:
            (student_id, assignment_id).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    @property
    def marks(self):
        """The mark given by the teacher.

        Returns:
            int, or None if not marked yet.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    @marks.setter
    def marks(self, value: int) -> None:
        """Set the mark after checking it.

        Args:
            value: the new mark.
        Raises:
            ValidationError: if value < 0 or value > max_marks.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    def is_late(self, assignment: Assignment) -> bool:
        """Check whether this was handed in after the deadline.

        Args:
            assignment: the Assignment it belongs to.
        Returns:
            True if submitted_at > assignment.deadline.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    def to_dict(self) -> dict:
        """The submission as one CSV row.

        Returns:
            dict with the columns of submissions.csv (blank marks if None).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")

    @classmethod
    def from_dict(cls, row: dict, max_marks: int) -> "Submission":
        """Build a Submission from one CSV row.

        Args:
            row: dict with the columns of submissions.csv.
            max_marks: from the matching Assignment.
        Returns:
            a new Submission (marked if the marks column is not blank).
        Raises:
            ValidationError: bad date, bad marks or missing column.
        Complexity: O(1).
        """
        raise NotImplementedError("Part 6")


def submit_work(submissions: dict, assignment: Assignment, student_id: str,
                text: str, now) -> Submission:
    """Record a new submission under the key (student_id, assignment_id).

    Args:
        submissions: {(student_id, assignment_id): Submission}.
        assignment: the Assignment being answered.
        student_id: who is submitting.
        text: the answer text.
        now: datetime.datetime of submission.
    Returns:
        the new Submission (late ones are accepted and flagged by is_late).
    Raises:
        DuplicateError: if this student already submitted.
        ValidationError: if text is empty.
    Complexity: O(1).
    """
    raise NotImplementedError("Part 6")


def pending_for_student(assignments: dict, submissions: dict,
                        student_id: str, course_ids: set) -> list[Assignment]:
    """Assignments in the student's courses that they have not submitted.

    Args:
        assignments: {assignment_id: Assignment}.
        submissions: {(student_id, assignment_id): Submission}.
        student_id: the student.
        course_ids: set of course IDs the student is enrolled in.
    Returns:
        list of Assignment, earliest deadline first.
    Complexity: O(a log a) for a assignments.
    """
    raise NotImplementedError("Part 6")
