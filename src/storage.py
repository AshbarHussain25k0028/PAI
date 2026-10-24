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

INTERFACE STUB (Part 1): bodies are written in Part 5.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # the repo folder
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


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
    raise NotImplementedError("Part 5")


def save_json(path, data) -> None:
    """Write data as JSON safely (temp file, then replace).

    Args:
        path: destination file.
        data: a list or dict made of plain values.
    Raises:
        DataFileError: if the file cannot be written.
    Complexity: O(n) for n characters written.
    """
    raise NotImplementedError("Part 5")


def load_csv(path) -> list[dict]:
    """Read a CSV file with a header row.

    Args:
        path: str or Path of the file.
    Returns:
        list of dicts, one per row (values are strings).
    Raises:
        DataFileError: file missing or unreadable.
    Complexity: O(r) for r rows.
    """
    raise NotImplementedError("Part 5")


def save_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    """Write rows to a CSV file safely (temp file, then replace).

    Args:
        path: destination file.
        rows: list of dicts.
        fieldnames: column order for the header.
    Raises:
        DataFileError: if the file cannot be written.
    Complexity: O(r) for r rows.
    """
    raise NotImplementedError("Part 5")


def data_dir() -> Path:
    """Pick the folder to read from.

    Returns:
        PROCESSED_DIR if it has users.json, otherwise RAW_DIR.
    Complexity: O(1).
    """
    raise NotImplementedError("Part 5")


class DataStore:
    """All LMS records in memory, each kept in a dict keyed by ID.

    Attributes:
        users (dict[str, User]), courses (dict[str, Course]),
        quizzes (dict[str, Quiz]), assignments (dict[str, Assignment]),
        submissions (dict[tuple[str, str], Submission]),
        attempts (list[dict])  -> kept in the order they happened.
    """

    def __init__(self):
        """Create an empty store (every dict and list starts empty).

        Complexity: O(1).
        """
        raise NotImplementedError("Part 5")

    def load(self, folder=None) -> None:
        """Fill the store from the data files.

        Args:
            folder: folder to read from; defaults to data_dir().
        Raises:
            DataFileError: a file is missing or malformed.
            ValidationError: a record has a bad value.
        Complexity: O(N) for N records in all files.
        """
        raise NotImplementedError("Part 5")

    def save(self, folder=None) -> None:
        """Write every record back to the data files.

        Args:
            folder: folder to write to; defaults to PROCESSED_DIR.
        Raises:
            DataFileError: if a file cannot be written.
        Complexity: O(N) for N records.
        """
        raise NotImplementedError("Part 5")

    def courses_for_student(self, student_id: str) -> list:
        """Courses the student is enrolled in.

        Args:
            student_id: e.g. "S01".
        Returns:
            list of Course objects.
        Complexity: O(c) for c courses (set lookup in each).
        """
        raise NotImplementedError("Part 5")

    def courses_for_teacher(self, teacher_id: str) -> list:
        """Courses taught by the teacher.

        Args:
            teacher_id: e.g. "T01".
        Returns:
            list of Course objects.
        Complexity: O(c) for c courses.
        """
        raise NotImplementedError("Part 5")
