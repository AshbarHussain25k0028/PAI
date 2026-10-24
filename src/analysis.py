"""Pandas progress report for teachers.

Owner: Ashbar Hussain (Part 11)
Lab concepts: Lab 08 (DataFrame, missing values, filtering, groupby, merge).

Key data structure
------------------
A Pandas DataFrame: a labelled table, one row per (student, quiz attempt)
or (student, submission). Cleaning, filtering and groupby work on the
whole table at once.

INTERFACE STUB (Part 1): bodies are written in Part 11.
"""

from __future__ import annotations


def build_progress_frame(attempts: list[dict], quizzes: dict):
    """One row per quiz attempt, with course and percentage columns.

    Args:
        attempts: records from attempts.json.
        quizzes: {quiz_id: Quiz}, used to add course_id.
    Returns:
        DataFrame with student_id, quiz_id, course_id, attempted_on,
        score, max_score, percent.
    Raises:
        ValidationError: if an attempt has an unknown quiz.
    Complexity: O(a) for a attempts.
    """
    raise NotImplementedError("Part 11")


def build_submission_frame(submissions: list[dict], assignments: dict):
    """One row per submission, with course, late flag and percentage.

    Args:
        submissions: rows from submissions.csv.
        assignments: {assignment_id: Assignment}.
    Returns:
        DataFrame with student_id, assignment_id, course_id, submitted_at,
        marks, max_marks, percent, late.
    Complexity: O(n) for n submissions.
    """
    raise NotImplementedError("Part 11")


def clean_frame(frame):
    """Clean a frame: drop exact duplicates, parse dates, turn blank marks
    into NaN (not zero, so "not marked" is not counted as a fail).

    Args:
        frame: a DataFrame from one of the build_* functions.
    Returns:
        a new, cleaned DataFrame.
    Complexity: O(n) for n rows.
    """
    raise NotImplementedError("Part 11")


def course_summary(progress):
    """Average quiz percent and attempt count per course (groupby).

    Args:
        progress: cleaned progress DataFrame.
    Returns:
        DataFrame indexed by course_id with mean_percent and attempts.
    Complexity: O(n) for n rows.
    """
    raise NotImplementedError("Part 11")


def topic_summary(attempts: list[dict], quizzes: dict):
    """Percent correct per course and topic, from the stored answers.

    Args:
        attempts: records from attempts.json.
        quizzes: {quiz_id: Quiz}.
    Returns:
        DataFrame with course_id, topic, correct, total, percent.
    Complexity: O(a * k) for a attempts of k questions.
    """
    raise NotImplementedError("Part 11")


def class_report(progress, submissions, course_id: str):
    """Merge quiz and assignment results for one course (one row per student).

    Args:
        progress: cleaned progress DataFrame.
        submissions: cleaned submission DataFrame.
        course_id: the course to report on.
    Returns:
        DataFrame with student_id, quiz_avg, assignment_avg, missing_work.
    Raises:
        NotFoundError: if the course has no records.
    Complexity: O(n) for n rows (merge on student_id).
    """
    raise NotImplementedError("Part 11")
