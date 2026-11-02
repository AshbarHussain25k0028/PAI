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
"""

from __future__ import annotations

from datetime import datetime

from exceptions import DuplicateError, ValidationError
from utils import format_datetime, parse_datetime, require_text

# Keys of assignments.json and columns of submissions.csv, in file order.
ASSIGNMENT_FIELDS = ("assignment_id", "course_id", "title", "deadline",
                     "max_marks")
SUBMISSION_FIELDS = ("student_id", "assignment_id", "submitted_at", "text",
                     "marks", "feedback")


def _whole_number(value, field: str) -> int:
    """Turn a value from a file or the keyboard into an int.

    Accepts an int (but not a bool) or text made only of digits, such as
    "9" or "-2" (the sign is checked later by the caller).

    Args:
        value: the value to check.
        field: the field name, used in the error message.
    Returns:
        the value as an int.
    Raises:
        ValidationError: if it is not a whole number.
    Complexity: O(k) for k characters.
    """
    # bool is a subclass of int in Python, so True would sneak through as 1.
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    raise ValidationError(f"'{field}' must be a whole number, got {value!r}.")


def _check_moment(value, field: str) -> datetime:
    """Check that a value is a datetime object.

    Args:
        value: the value to check.
        field: the field name, used in the error message.
    Returns:
        the same datetime.
    Raises:
        ValidationError: if it is not a datetime.
    Complexity: O(1).
    """
    if not isinstance(value, datetime):
        raise ValidationError(f"'{field}' must be a date and time.")
    return value


def _check_max_marks(value) -> int:
    """Check that the maximum mark is a whole number above 0.

    Args:
        value: the maximum mark (int or digit text).
    Returns:
        the maximum as an int.
    Raises:
        ValidationError: if it is not a whole number or is 0 or less.
    Complexity: O(1).
    """
    max_marks = _whole_number(value, "max_marks")
    if max_marks <= 0:
        raise ValidationError(f"'max_marks' must be above 0, got {max_marks}.")
    return max_marks


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
        self.assignment_id = require_text(assignment_id, "assignment_id")
        self.course_id = require_text(course_id, "course_id")
        self.title = require_text(title, "title")
        self.deadline = _check_moment(deadline, "deadline")
        self.max_marks = _check_max_marks(max_marks)

    def __repr__(self) -> str:
        """Short text form, handy when printing in the console.

        Returns:
            e.g. "Assignment(AS01, 'Gradebook', due 2026-10-20 23:59)".
        Complexity: O(1).
        """
        return (f"Assignment({self.assignment_id}, {self.title!r}, "
                f"due {format_datetime(self.deadline)})")

    def is_open(self, now) -> bool:
        """Check whether the deadline has not passed yet.

        Args:
            now: datetime.datetime to compare with.
        Returns:
            True if now <= deadline.
        Complexity: O(1).
        """
        return now <= self.deadline

    def to_dict(self) -> dict:
        """The assignment as a plain dict for JSON.

        Returns:
            dict with the keys of assignments.json (deadline as text).
        Complexity: O(1).
        """
        record = {field: getattr(self, field) for field in ASSIGNMENT_FIELDS}
        record["deadline"] = format_datetime(self.deadline)
        return record

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
        if not isinstance(record, dict):
            raise ValidationError("Each assignment must be a dict of fields.")
        deadline = require_text(record.get("deadline"), "deadline")
        return cls(record.get("assignment_id"), record.get("course_id"),
                   record.get("title"), parse_datetime(deadline),
                   record.get("max_marks"))


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
            ValidationError: if an ID or the text is empty, the date is not
                a datetime, or max_marks <= 0.
        Complexity: O(1).
        """
        self.student_id = require_text(student_id, "student_id")
        self.assignment_id = require_text(assignment_id, "assignment_id")
        self.submitted_at = _check_moment(submitted_at, "submitted_at")
        self.text = require_text(text, "text")
        self.max_marks = _check_max_marks(max_marks)
        self._marks = None       # protected: only the marks setter changes it
        self.feedback = ""

    def __repr__(self) -> str:
        """Short text form, handy when printing in the console.

        Returns:
            e.g. "Submission(S01, AS01, marks=9/10)".
        Complexity: O(1).
        """
        if self._marks is None:
            shown = "unmarked"
        else:
            shown = f"{self._marks}/{self.max_marks}"
        return f"Submission({self.student_id}, {self.assignment_id}, marks={shown})"

    @property
    def key(self) -> tuple:
        """The dict key of this submission.

        Returns:
            (student_id, assignment_id).
        Complexity: O(1).
        """
        return (self.student_id, self.assignment_id)

    @property
    def marks(self):
        """The mark given by the teacher.

        Returns:
            int, or None if not marked yet.
        Complexity: O(1).
        """
        return self._marks

    @marks.setter
    def marks(self, value: int) -> None:
        """Set the mark after checking it.

        Args:
            value: the new mark.
        Raises:
            ValidationError: if value < 0 or value > max_marks.
        Complexity: O(1).
        """
        value = _whole_number(value, "marks")
        if not 0 <= value <= self.max_marks:
            raise ValidationError(
                f"Marks must be from 0 to {self.max_marks}, got {value}.")
        self._marks = value

    def is_late(self, assignment: Assignment) -> bool:
        """Check whether this was handed in after the deadline.

        Args:
            assignment: the Assignment it belongs to.
        Returns:
            True if submitted_at > assignment.deadline.
        Complexity: O(1).
        """
        return self.submitted_at > assignment.deadline

    def to_dict(self) -> dict:
        """The submission as one CSV row.

        Returns:
            dict with the columns of submissions.csv (blank marks if None).
        Complexity: O(1).
        """
        return {"student_id": self.student_id,
                "assignment_id": self.assignment_id,
                "submitted_at": format_datetime(self.submitted_at),
                "text": self.text,
                "marks": "" if self._marks is None else self._marks,
                "feedback": self.feedback}

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
        if not isinstance(row, dict):
            raise ValidationError("Each submission must be a dict of columns.")
        submitted_at = require_text(row.get("submitted_at"), "submitted_at")
        submission = cls(row.get("student_id"), row.get("assignment_id"),
                         parse_datetime(submitted_at), row.get("text"),
                         max_marks)
        marks = row.get("marks")
        if marks is not None and str(marks).strip():
            submission.marks = marks          # goes through the checked setter
        submission.feedback = (row.get("feedback") or "").strip()
        return submission


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
    submission = Submission(student_id, assignment.assignment_id, now, text,
                            assignment.max_marks)
    if submission.key in submissions:
        raise DuplicateError(
            f"{submission.student_id} has already submitted "
            f"{assignment.assignment_id}.")
    submissions[submission.key] = submission
    return submission


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
    pending = [assignment for assignment in assignments.values()
               if assignment.course_id in course_ids
               and (student_id, assignment.assignment_id) not in submissions]
    return sorted(pending, key=lambda assignment: assignment.deadline)
