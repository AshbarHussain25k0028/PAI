"""Loading and saving LMS records as JSON and CSV files.

Owner: Ashbar Hussain (Part 5)
Lab concepts: Lab 06 (files with `with`, JSON, CSV, specific exceptions).

Where the data lives
--------------------
- The app reads from data/processed/ if users.json exists there, otherwise
  from data/raw/ (the fictional sample data).
- It always saves to data/processed/, so data/raw/ stays clean.
- A safe save writes a temporary file first and then replaces the old one,
  so a crash half-way never leaves a broken file.

Key data structure: DataStore keeps one dict per record type,
{id: object}, so every lookup by ID is O(1).

Assignments and submissions are kept as plain dicts (the JSON/CSV records)
until Part 6 adds the Assignment and Submission classes.
"""

from __future__ import annotations

import contextlib
import csv
import json
import os
from pathlib import Path

from courses import COURSE_FIELDS, MATERIAL_FIELDS, Course, Material
from exceptions import DataFileError, DuplicateError, ValidationError
from quizzes import Quiz
from users import user_from_dict

ROOT = Path(__file__).resolve().parent.parent      # the repo folder
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# One file name per record type, the same in data/raw and data/processed.
USERS_FILE = "users.json"
COURSES_FILE = "courses.csv"
ENROLLMENTS_FILE = "enrollments.csv"
MATERIALS_FILE = "materials.csv"
QUIZZES_FILE = "quizzes.json"
ATTEMPTS_FILE = "attempts.json"
ASSIGNMENTS_FILE = "assignments.json"
SUBMISSIONS_FILE = "submissions.csv"

# Column order of the CSV files that no other module owns.
ENROLLMENT_FIELDS = ("student_id", "course_id")
SUBMISSION_FIELDS = ("student_id", "assignment_id", "submitted_at", "text",
                     "marks", "feedback")


def load_json(path):
    """Read a JSON file.

    Args:
        path: str or Path of the file.
    Returns:
        the parsed list or dict.
    Raises:
        DataFileError: file missing, unreadable or not valid JSON.
    Complexity: O(n) for n characters.
    """
    path = Path(path)
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise DataFileError(f"File not found: {path}") from error
    except json.JSONDecodeError as error:
        raise DataFileError(
            f"{path.name} is not valid JSON (line {error.lineno}).") from error
    except (OSError, UnicodeDecodeError) as error:
        raise DataFileError(f"Could not read {path.name}: {error}") from error


def _safe_write(path, write_body) -> None:
    """Write a file through a temporary copy, then swap it into place.

    os.replace() is atomic, so readers see either the old file or the
    complete new one, never a half-written file.

    Args:
        path: destination file.
        write_body: function that takes the open temp file and writes to it.
    Raises:
        DataFileError: if the folder or file cannot be written, or the data
            cannot be turned into text.
    Complexity: O(n) for n characters written.
    """
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp, "w", encoding="utf-8", newline="") as file:
            write_body(file)
        os.replace(temp, path)
    except (OSError, TypeError, ValueError) as error:
        with contextlib.suppress(OSError):
            temp.unlink(missing_ok=True)      # do not leave the temp file behind
        raise DataFileError(f"Could not save {path.name}: {error}") from error


def save_json(path, data) -> None:
    """Write data as JSON safely (temp file, then replace).

    Args:
        path: destination file.
        data: a list or dict made of plain values.
    Raises:
        DataFileError: if the file cannot be written.
    Complexity: O(n) for n characters written.
    """
    _safe_write(path, lambda file: json.dump(data, file, indent=2,
                                             ensure_ascii=False))


def load_csv(path) -> list[dict]:
    """Read a CSV file with a header row.

    Args:
        path: str or Path of the file.
    Returns:
        list of dicts, one per row (values are strings; a missing value
        becomes "" and extra values without a header are dropped).
    Raises:
        DataFileError: file missing or unreadable.
    Complexity: O(r) for r rows.
    """
    path = Path(path)
    try:
        with open(path, encoding="utf-8", newline="") as file:
            return [{key: value if value is not None else ""
                     for key, value in row.items() if key is not None}
                    for row in csv.DictReader(file)]
    except FileNotFoundError as error:
        raise DataFileError(f"File not found: {path}") from error
    except (csv.Error, OSError, UnicodeDecodeError) as error:
        raise DataFileError(f"Could not read {path.name}: {error}") from error


def save_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    """Write rows to a CSV file safely (temp file, then replace).

    Args:
        path: destination file.
        rows: list of dicts.
        fieldnames: column order for the header.
    Raises:
        DataFileError: if the file cannot be written, or a row has a
            column that is not in fieldnames.
    Complexity: O(r) for r rows.
    """
    def write_rows(file):
        writer = csv.DictWriter(file, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)

    _safe_write(path, write_rows)


def data_dir() -> Path:
    """Pick the folder to read from.

    Returns:
        PROCESSED_DIR if it has users.json, otherwise RAW_DIR.
    Complexity: O(1).
    """
    if (PROCESSED_DIR / USERS_FILE).is_file():
        return PROCESSED_DIR
    return RAW_DIR


def _records(data, file_name: str) -> list[dict]:
    """Check that a loaded JSON file is a list of dicts.

    Args:
        data: what load_json() returned.
        file_name: used in the error message.
    Returns:
        the same list.
    Raises:
        DataFileError: if it is not a list of dicts.
    Complexity: O(n) for n records.
    """
    if not isinstance(data, list) or not all(
            isinstance(record, dict) for record in data):
        raise DataFileError(f"{file_name} must hold a list of records.")
    return data


def _add_unique(table: dict, key, value, label: str) -> None:
    """Put value into table[key], refusing a key that is already there.

    Args:
        table: one of the DataStore dicts.
        key: the record's ID (or tuple key).
        value: the object or record to store.
        label: kind of record, for the error message.
    Raises:
        DuplicateError: if the key already exists.
    Complexity: O(1).
    """
    if key in table:
        raise DuplicateError(f"Duplicate {label} {key} in the data files.")
    table[key] = value


def _as_record(item) -> dict:
    """Turn an object (or an existing plain record) into a dict for saving.

    Args:
        item: anything with a to_dict() method, or a dict.
    Returns:
        a plain dict.
    Complexity: O(1).
    """
    return item.to_dict() if hasattr(item, "to_dict") else dict(item)


class DataStore:
    """All LMS records in memory, each kept in a dict keyed by ID.

    Attributes:
        users (dict[str, User]), courses (dict[str, Course]),
        quizzes (dict[str, Quiz]),
        assignments (dict[str, dict])  -> plain records until Part 6,
        submissions (dict[tuple[str, str], dict]) -> key (student_id,
            assignment_id); plain rows until Part 6,
        attempts (list[dict])  -> kept in the order they happened.
    """

    def __init__(self):
        """Create an empty store (every dict and list starts empty).

        Complexity: O(1).
        """
        self.users: dict = {}          # "S01" -> Student, "T01" -> Teacher ...
        self.courses: dict = {}        # "C101" -> Course
        self.quizzes: dict = {}        # "Q01" -> Quiz
        self.assignments: dict = {}    # "AS01" -> assignment record
        self.submissions: dict = {}    # ("S01", "AS01") -> submission row
        self.attempts: list = []       # quiz attempts, oldest first

    def load(self, folder=None) -> None:
        """Fill the store from the data files.

        Users and courses come first, because the other files refer to them.

        Args:
            folder: folder to read from; defaults to data_dir().
        Raises:
            DataFileError: a file is missing or malformed.
            ValidationError: a record has a bad value.
            DuplicateError: two records share an ID.
        Complexity: O(N) for N records in all files.
        """
        folder = Path(folder) if folder is not None else data_dir()
        self.__init__()                # start empty, so load() can be repeated
        self._load_users(folder)
        self._load_courses(folder)
        self._load_quizzes(folder)
        self._load_attempts(folder)
        self._load_assignments(folder)
        self._load_submissions(folder)

    def _need(self, table: dict, key: str, label: str):
        """Return table[key], or explain which reference is broken.

        Args:
            table: the dict to look in.
            key: the ID a record refers to.
            label: kind of record, for the error message.
        Returns:
            the stored object.
        Raises:
            ValidationError: if key is not in table.
        Complexity: O(1).
        """
        if key not in table:
            raise ValidationError(f"Unknown {label} '{key}' in the data files.")
        return table[key]

    def _load_users(self, folder: Path) -> None:
        """Read users.json into self.users.

        Args:
            folder: data folder.
        Complexity: O(u) for u users.
        """
        for record in _records(load_json(folder / USERS_FILE), USERS_FILE):
            user = user_from_dict(record)
            _add_unique(self.users, user.user_id, user, "user")

    def _load_courses(self, folder: Path) -> None:
        """Read courses.csv, then the enrollments and materials of each course.

        Args:
            folder: data folder.
        Complexity: O(c) for c courses, plus the two helpers below.
        """
        for row in load_csv(folder / COURSES_FILE):
            course = Course.from_dict(row)
            self._need(self.users, course.teacher_id, "teacher")
            _add_unique(self.courses, course.course_id, course, "course")
        self._load_enrollments(folder)
        self._load_materials(folder)

    def _load_enrollments(self, folder: Path) -> None:
        """Read enrollments.csv into each course's enrolled set.

        Args:
            folder: data folder.
        Complexity: O(e) for e enrollments (set add is O(1)).
        """
        for row in load_csv(folder / ENROLLMENTS_FILE):
            course = self._need(self.courses, row.get("course_id"), "course")
            student_id = row.get("student_id")
            self._need(self.users, student_id, "student")
            if not course.enroll(student_id):
                raise DuplicateError(
                    f"{student_id} is enrolled twice in {course.course_id}.")

    def _load_materials(self, folder: Path) -> None:
        """Read materials.csv into each course's materials list.

        Args:
            folder: data folder.
        Complexity: O(m * k) for m materials (k per course, for the
        duplicate check in add_material).
        """
        for row in load_csv(folder / MATERIALS_FILE):
            material = Material.from_dict(row)
            self._need(self.courses, material.course_id,
                       "course").add_material(material)

    def _load_quizzes(self, folder: Path) -> None:
        """Read quizzes.json into self.quizzes.

        Args:
            folder: data folder.
        Complexity: O(q * n) for q quizzes of n questions.
        """
        for record in _records(load_json(folder / QUIZZES_FILE), QUIZZES_FILE):
            quiz = Quiz.from_dict(record)
            self._need(self.courses, quiz.course_id, "course")
            _add_unique(self.quizzes, quiz.quiz_id, quiz, "quiz")

    def _load_attempts(self, folder: Path) -> None:
        """Read attempts.json into self.attempts, keeping the file order.

        Args:
            folder: data folder.
        Complexity: O(a) for a attempts.
        """
        records = _records(load_json(folder / ATTEMPTS_FILE), ATTEMPTS_FILE)
        for record in records:
            self._need(self.users, record.get("student_id"), "student")
            self._need(self.quizzes, record.get("quiz_id"), "quiz")
        self.attempts = list(records)

    def _load_assignments(self, folder: Path) -> None:
        """Read assignments.json into self.assignments (plain records).

        Args:
            folder: data folder.
        Complexity: O(a) for a assignments.
        """
        records = _records(load_json(folder / ASSIGNMENTS_FILE),
                           ASSIGNMENTS_FILE)
        for record in records:
            self._need(self.courses, record.get("course_id"), "course")
            _add_unique(self.assignments, record.get("assignment_id"),
                        record, "assignment")

    def _load_submissions(self, folder: Path) -> None:
        """Read submissions.csv into self.submissions, keyed by a tuple.

        Args:
            folder: data folder.
        Complexity: O(s) for s submissions.
        """
        for row in load_csv(folder / SUBMISSIONS_FILE):
            key = (row.get("student_id"), row.get("assignment_id"))
            self._need(self.users, key[0], "student")
            self._need(self.assignments, key[1], "assignment")
            _add_unique(self.submissions, key, row, "submission")

    def save(self, folder=None) -> None:
        """Write every record back to the data files.

        users.json is written last: data_dir() only switches to the
        processed folder once every other file is already there.

        Args:
            folder: folder to write to; defaults to PROCESSED_DIR.
        Raises:
            DataFileError: if a file cannot be written.
        Complexity: O(N) for N records.
        """
        folder = Path(folder) if folder is not None else PROCESSED_DIR
        courses = list(self.courses.values())
        save_csv(folder / COURSES_FILE, [c.to_dict() for c in courses],
                 COURSE_FIELDS)
        save_csv(folder / ENROLLMENTS_FILE, self._enrollment_rows(),
                 ENROLLMENT_FIELDS)
        save_csv(folder / MATERIALS_FILE,
                 [m.to_dict() for c in courses for m in c.materials],
                 MATERIAL_FIELDS)
        save_json(folder / QUIZZES_FILE,
                  [quiz.to_dict() for quiz in self.quizzes.values()])
        save_json(folder / ATTEMPTS_FILE, self.attempts)
        save_json(folder / ASSIGNMENTS_FILE,
                  [_as_record(item) for item in self.assignments.values()])
        save_csv(folder / SUBMISSIONS_FILE,
                 [_as_record(item) for item in self.submissions.values()],
                 SUBMISSION_FIELDS)
        save_json(folder / USERS_FILE,
                  [user.to_dict() for user in self.users.values()])

    def _enrollment_rows(self) -> list[dict]:
        """One {"student_id", "course_id"} row per enrolled student.

        Students are sorted so the saved file is the same on every run
        (a set has no fixed order).

        Returns:
            list of dicts in course order, then student ID order.
        Complexity: O(e log e) for e enrollments.
        """
        return [{"student_id": student_id, "course_id": course.course_id}
                for course in self.courses.values()
                for student_id in sorted(course.enrolled)]

    def courses_for_student(self, student_id: str) -> list:
        """Courses the student is enrolled in.

        Args:
            student_id: e.g. "S01".
        Returns:
            list of Course objects.
        Complexity: O(c) for c courses (set lookup in each).
        """
        return [course for course in self.courses.values()
                if course.is_enrolled(student_id)]

    def courses_for_teacher(self, teacher_id: str) -> list:
        """Courses taught by the teacher.

        Args:
            teacher_id: e.g. "T01".
        Returns:
            list of Course objects.
        Complexity: O(c) for c courses.
        """
        return [course for course in self.courses.values()
                if course.teacher_id == teacher_id]
