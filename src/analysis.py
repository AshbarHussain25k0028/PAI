"""Pandas progress report for teachers.

Owner: Ashbar Hussain (Part 11)
Lab concepts: Lab 08 (DataFrame, missing values, filtering, groupby, merge).

Key data structure
------------------
A Pandas DataFrame: a labelled table, one row per (student, quiz attempt)
or (student, submission). Cleaning, filtering and groupby work on the
whole table at once.

    progress frame    -> student_id, quiz_id, course_id, attempted_on,
                         score, max_score, percent
    submission frame  -> student_id, assignment_id, course_id, submitted_at,
                         marks, max_marks, percent, late

A blank mark (not marked yet) becomes NaN, not 0, so "not marked" is never
counted as a fail. Pandas skips NaN when it takes a mean.

Run `python src/analysis.py` to print the class report of every course.
"""

from __future__ import annotations

import pandas as pd

from exceptions import LMSError, NotFoundError, ValidationError

DATE_FORMAT = "%Y-%m-%d %H:%M"      # same format as the JSON and CSV files
PASS_MARK = 60.0                    # percent; below this a student needs help

PROGRESS_COLUMNS = ["student_id", "quiz_id", "course_id", "attempted_on",
                    "score", "max_score", "percent"]
SUBMISSION_COLUMNS = ["student_id", "assignment_id", "course_id",
                      "submitted_at", "marks", "max_marks", "percent", "late"]
REPORT_COLUMNS = ["student_id", "quiz_avg", "assignment_avg", "missing_work"]

DATE_COLUMNS = ("attempted_on", "submitted_at")
NUMBER_COLUMNS = ("score", "max_score", "marks", "max_marks")
# (points column, maximum column) used to work out the percent column
PERCENT_SOURCES = (("score", "max_score"), ("marks", "max_marks"))


def _course_column(ids: pd.Series, course_of: dict, label: str) -> pd.Series:
    """Look up the course of every quiz or assignment ID in one step.

    Args:
        ids: column of quiz or assignment IDs.
        course_of: {id: course_id}.
        label: "quiz" or "assignment", for the error message.
    Returns:
        Series of course IDs, in the same row order.
    Raises:
        ValidationError: if an ID is not in course_of.
    Complexity: O(n) for n rows.
    """
    courses = ids.map(course_of)
    unknown = sorted(set(ids[courses.isna()].astype(str)))
    if unknown:
        raise ValidationError(f"Unknown {label} ID(s): {', '.join(unknown)}.")
    return courses


def _percent(points: pd.Series, maximum: pd.Series) -> pd.Series:
    """Turn points into a percentage of the maximum (broadcast, no loop).

    Args:
        points: score or marks column (NaN allowed).
        maximum: matching max_score or max_marks column.
    Returns:
        Series of percentages, NaN where points is NaN.
    Complexity: O(n) for n rows.
    """
    points = pd.to_numeric(points, errors="coerce")
    maximum = pd.to_numeric(maximum, errors="coerce")
    return points / maximum * 100


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
    if not isinstance(attempts, list):
        raise ValidationError("attempts must be a list of records.")
    frame = pd.DataFrame(attempts, columns=PROGRESS_COLUMNS[:-1])
    course_of = {quiz_id: quiz.course_id for quiz_id, quiz in quizzes.items()}
    frame["course_id"] = _course_column(frame["quiz_id"], course_of, "quiz")
    frame["percent"] = _percent(frame["score"], frame["max_score"])
    return frame


def build_submission_frame(submissions: list[dict], assignments: dict):
    """One row per submission, with course, late flag and percentage.

    Args:
        submissions: rows from submissions.csv.
        assignments: {assignment_id: Assignment}.
    Returns:
        DataFrame with student_id, assignment_id, course_id, submitted_at,
        marks, max_marks, percent, late.
    Raises:
        ValidationError: if a row has an unknown assignment.
    Complexity: O(n) for n submissions.
    """
    if not isinstance(submissions, list):
        raise ValidationError("submissions must be a list of rows.")
    frame = pd.DataFrame(submissions,
                         columns=["student_id", "assignment_id", "submitted_at", "marks"])
    ids = frame["assignment_id"]
    frame["course_id"] = _course_column(
        ids, {key: a.course_id for key, a in assignments.items()}, "assignment")
    frame["max_marks"] = ids.map({key: a.max_marks for key, a in assignments.items()})
    frame["percent"] = _percent(frame["marks"], frame["max_marks"])
    handed_in = pd.to_datetime(frame["submitted_at"], format=DATE_FORMAT, errors="coerce")
    deadline = ids.map({key: a.deadline for key, a in assignments.items()})
    frame["late"] = handed_in > pd.to_datetime(deadline)
    return frame[SUBMISSION_COLUMNS]


def clean_frame(frame):
    """Clean a frame: drop exact duplicates, parse dates, turn blank marks
    into NaN (not zero, so "not marked" is not counted as a fail).

    Rows without a student_id are dropped, IDs are trimmed and upper-cased,
    and the percent column is worked out again from the cleaned numbers.

    Args:
        frame: a DataFrame from one of the build_* functions.
    Returns:
        a new, cleaned DataFrame (the input is not changed).
    Raises:
        ValidationError: if frame is not a DataFrame.
    Complexity: O(n) for n rows.
    """
    if not isinstance(frame, pd.DataFrame):
        raise ValidationError("clean_frame needs a DataFrame.")
    cleaned = frame.copy()
    for column in cleaned.columns:
        if column.endswith("_id"):
            cleaned[column] = cleaned[column].astype("string").str.strip().str.upper()
        elif column in DATE_COLUMNS:
            cleaned[column] = pd.to_datetime(cleaned[column], format=DATE_FORMAT,
                                             errors="coerce")
        elif column in NUMBER_COLUMNS:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    cleaned = cleaned.replace("", pd.NA).dropna(subset=["student_id"])
    for points, maximum in PERCENT_SOURCES:
        if points in cleaned.columns:
            cleaned["percent"] = _percent(cleaned[points], cleaned[maximum])
    return cleaned.drop_duplicates().reset_index(drop=True)


def latest_only(progress):
    """Keep only each student's newest attempt at each quiz.

    Args:
        progress: cleaned progress DataFrame.
    Returns:
        DataFrame with one row per (student_id, quiz_id).
    Complexity: O(n log n) for n rows (sort by date).
    """
    ordered = progress.sort_values("attempted_on", kind="stable")
    return ordered.drop_duplicates(subset=["student_id", "quiz_id"], keep="last")


def course_summary(progress):
    """Average quiz percent and attempt count per course (groupby).

    Args:
        progress: cleaned progress DataFrame.
    Returns:
        DataFrame indexed by course_id with mean_percent and attempts.
    Complexity: O(n) for n rows.
    """
    summary = progress.groupby("course_id").agg(
        mean_percent=("percent", "mean"), attempts=("quiz_id", "size"))
    summary["mean_percent"] = summary["mean_percent"].round(1)
    return summary


def _latest_records(attempts: list[dict]) -> dict:
    """The newest attempt for every (student, quiz) pair.

    Args:
        attempts: records from attempts.json.
    Returns:
        dict {(student_id, quiz_id): attempt record}.
    Complexity: O(a log a) for a attempts (sorted by date text, which
        sorts correctly because the format is YYYY-MM-DD HH:MM).
    """
    latest = {}   # (student_id, quiz_id) -> record; a later one overwrites
    for record in sorted(attempts, key=lambda r: str(r.get("attempted_on", ""))):
        latest[(record.get("student_id"), record.get("quiz_id"))] = record
    return latest


def topic_summary(attempts: list[dict], quizzes: dict):
    """Percent correct per course and topic, from the stored answers.

    Only the newest attempt of each student at each quiz is counted.

    Args:
        attempts: records from attempts.json.
        quizzes: {quiz_id: Quiz}.
    Returns:
        DataFrame with course_id, topic, correct, total, percent.
    Raises:
        ValidationError: unknown quiz, or answers that do not fit the quiz.
    Complexity: O(a * k) for a attempts of k questions.
    """
    rows = []
    for (_, quiz_id), record in _latest_records(attempts).items():
        if quiz_id not in quizzes:
            raise ValidationError(f"Unknown quiz ID: {quiz_id}.")
        quiz = quizzes[quiz_id]
        for topic, (correct, total) in quiz.grade_attempt(record.get("answers"))[1].items():
            rows.append({"course_id": quiz.course_id, "topic": topic,
                         "correct": correct, "total": total})
    frame = pd.DataFrame(rows, columns=["course_id", "topic", "correct", "total"])
    table = frame.groupby(["course_id", "topic"], as_index=False)[["correct", "total"]].sum()
    table["percent"] = _percent(table["correct"], table["total"]).round(1)
    return table


def _quiz_table(progress, course_id: str):
    """Per-student quiz average in one course (newest attempts only).

    Args:
        progress: cleaned progress DataFrame.
        course_id: the course.
    Returns:
        (DataFrame indexed by student_id with quiz_avg and quizzes_done,
         number of different quizzes in the course's records).
    Complexity: O(n log n) for n rows.
    """
    rows = latest_only(progress[progress["course_id"] == course_id])
    table = rows.groupby("student_id").agg(quiz_avg=("percent", "mean"),
                                           quizzes_done=("quiz_id", "nunique"))
    return table, rows["quiz_id"].nunique()


def _work_table(submissions, course_id: str):
    """Per-student assignment average in one course.

    Unmarked work is NaN, so it is skipped by the mean, not counted as 0.

    Args:
        submissions: cleaned submission DataFrame.
        course_id: the course.
    Returns:
        (DataFrame indexed by student_id with assignment_avg and submitted,
         number of different assignments in the course's records).
    Complexity: O(n) for n rows.
    """
    rows = submissions[submissions["course_id"] == course_id]
    table = rows.groupby("student_id").agg(assignment_avg=("percent", "mean"),
                                           submitted=("assignment_id", "nunique"))
    return table, rows["assignment_id"].nunique()


def class_report(progress, submissions, course_id: str, enrolled=None):
    """Merge quiz and assignment results for one course (one row per student).

    Args:
        progress: cleaned progress DataFrame.
        submissions: cleaned submission DataFrame.
        course_id: the course to report on.
        enrolled: optional set of enrolled student IDs; when given, the
            report lists exactly these students (even with no work at all).
    Returns:
        DataFrame with student_id, quiz_avg, assignment_avg, missing_work
        (quizzes not attempted + assignments not submitted).
    Raises:
        NotFoundError: if the course has no records.
    Complexity: O(n) for n rows (merge on student_id).
    """
    course_id = str(course_id).strip().upper()
    quiz_table, quiz_count = _quiz_table(progress, course_id)
    work_table, work_count = _work_table(submissions, course_id)
    if quiz_table.empty and work_table.empty:
        raise NotFoundError(f"No quiz or assignment records for {course_id}.")
    report = pd.merge(quiz_table, work_table, on="student_id", how="outer")
    if enrolled is not None:
        report = report.reindex(sorted(enrolled))
    done = report["quizzes_done"].fillna(0) + report["submitted"].fillna(0)
    report["missing_work"] = (quiz_count + work_count - done).astype(int)
    report = report.round(1).rename_axis("student_id").reset_index()
    return report[REPORT_COLUMNS]


def needs_attention(report, pass_mark: float = PASS_MARK):
    """Filter the students below the pass mark or with missing work.

    Args:
        report: DataFrame from class_report().
        pass_mark: percent, 0-100.
    Returns:
        the matching rows, weakest quiz average first.
    Raises:
        ValidationError: if pass_mark is not a number from 0 to 100.
    Complexity: O(n log n) for n students.
    """
    if isinstance(pass_mark, bool) or not isinstance(pass_mark, (int, float)) \
            or not 0 <= pass_mark <= 100:
        raise ValidationError("The pass mark must be a number from 0 to 100.")
    weak = ((report["quiz_avg"] < pass_mark) | (report["assignment_avg"] < pass_mark)
            | (report["missing_work"] > 0))
    return report[weak].sort_values("quiz_avg", na_position="first")


def frames_from_store(store) -> tuple:
    """Build and clean both frames from the loaded data.

    Args:
        store: the loaded DataStore.
    Returns:
        (progress, submissions) cleaned DataFrames.
    Raises:
        ValidationError: if a record refers to an unknown quiz or assignment.
    Complexity: O(a + s) for a attempts and s submissions.
    """
    progress = clean_frame(build_progress_frame(store.attempts, store.quizzes))
    rows = [submission.to_dict() for submission in store.submissions.values()]
    submissions = clean_frame(build_submission_frame(rows, store.assignments))
    return progress, submissions


def _show(frame) -> str:
    """Format a DataFrame for the console: no index, '-' for missing.

    Args:
        frame: any DataFrame.
    Returns:
        the table as text.
    Complexity: O(n) for n cells.
    """
    return frame.to_string(index=False, na_rep="-", float_format=lambda v: f"{v:.1f}")


def _print_topics(store, course_id: str) -> None:
    """Print percent correct per topic for one course, weakest first.

    Args:
        store: the loaded DataStore (attempts and quizzes).
        course_id: the course.
    Complexity: O(a * k) for a attempts of k questions.
    """
    topics = topic_summary(store.attempts, store.quizzes)
    topics = topics[topics["course_id"] == course_id].drop(columns="course_id")
    if not topics.empty:
        print("\nPercent correct by topic:\n" + _show(topics.sort_values("percent")))


def print_class_report(store, course) -> None:
    """Print the course summary, topic table and per-student report.

    Args:
        store: the loaded DataStore.
        course: the Course to report on.
    Raises:
        NotFoundError: if the course has no quiz or assignment records.
        ValidationError: if a record refers to an unknown quiz or assignment.
    Complexity: O(a * k + s + n log n) for a attempts of k questions,
        s submissions and n students.
    """
    progress, submissions = frames_from_store(store)
    report = class_report(progress, submissions, course.course_id, course.enrolled)
    names = {user_id: user.name for user_id, user in store.users.items()}
    report.insert(1, "name", report["student_id"].map(names))
    print(f"\nClass report: {course.course_id} {course.title}")
    summary = course_summary(progress)
    if course.course_id in summary.index:
        row = summary.loc[course.course_id]
        print(f"Quiz average {row['mean_percent']:.1f}% over {int(row['attempts'])} attempts.")
    _print_topics(store, course.course_id)
    print("\nStudents (percent, '-' = nothing to average):\n" + _show(report))
    weak = needs_attention(report)
    print(f"\nNeed attention (below {PASS_MARK:.0f}% or missing work): "
          + (", ".join(weak["student_id"]) if not weak.empty else "none"))


if __name__ == "__main__":
    from storage import DataStore
    try:
        lms = DataStore()
        lms.load()
        for lms_course in lms.courses.values():
            print_class_report(lms, lms_course)
    except LMSError as error:
        print(f"Could not build the class report: {error}")
