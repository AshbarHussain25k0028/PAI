"""Quiz scores as a NumPy matrix (students x quizzes).

Owner: Muhammad Mudassir (Part 10)
Lab concepts: Lab 07 (2-D arrays, boolean masks, NaN, broadcasting,
mean along an axis, vectorisation instead of loops).

Key data structure
------------------
A 2-D float array: one row per student, one column per quiz.
A missing attempt is NaN, so it is not counted as a zero.
All maths on the matrix is vectorised: no Python loop over the elements.

    rows    -> student_ids, e.g. ["S01", "S02", ...]   (axis 0)
    columns -> quiz_ids,    e.g. ["Q01", "Q02"]        (axis 1)
    matrix[1, 0] -> S02's score on Q01 (NaN if S02 never took Q01)

Run `python src/scores.py` to print the class score table of each course
and the loop vs vectorised timing.
"""

from __future__ import annotations

import time

import numpy as np

from exceptions import LMSError, ValidationError


def _positions(ids: list[str], label: str) -> dict[str, int]:
    """Map each ID to its row or column number.

    Args:
        ids: student or quiz IDs, in matrix order.
        label: "student" or "quiz", for the error message.
    Returns:
        dict {id: index}, e.g. {"S01": 0, "S02": 1}.
    Raises:
        ValidationError: if an ID appears twice (the order would be unclear).
    Complexity: O(n) for n IDs.
    """
    positions = {item_id: index for index, item_id in enumerate(ids)}
    if len(positions) != len(ids):
        raise ValidationError(f"The {label} IDs contain a duplicate.")
    return positions


def _latest_scores(attempts: list[dict]) -> dict[tuple[str, str], float]:
    """Keep only the newest attempt of each (student, quiz) pair.

    "YYYY-MM-DD HH:MM" strings sort in time order, so after sorting, a later
    attempt simply overwrites an earlier one in the dict.

    Args:
        attempts: records from attempts.json.
    Returns:
        dict {(student_id, quiz_id): score}.
    Raises:
        ValidationError: if a record is missing a field.
    Complexity: O(a log a) for a attempts (the sort).
    """
    try:
        ordered = sorted(attempts, key=lambda record: record["attempted_on"])
        return {(record["student_id"], record["quiz_id"]): float(record["score"])
                for record in ordered}
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError(f"Bad attempt record: {error}") from error


def score_matrix(attempts: list[dict], student_ids: list[str],
                 quiz_ids: list[str]):
    """Build the students x quizzes score matrix.

    The matrix starts full of NaN. The row and column number of every attempt
    are collected into two index arrays, and all scores are placed in one
    vectorised step: matrix[rows, cols] = scores.

    Args:
        attempts: records from attempts.json.
        student_ids: row order.
        quiz_ids: column order.
    Returns:
        numpy array of shape (len(student_ids), len(quiz_ids)); NaN where a
        student has no attempt (the latest attempt wins if there are two).
    Raises:
        ValidationError: if an attempt has an unknown student or quiz, a
            record is incomplete, or an ID list has a duplicate.
    Complexity: O(a log a + s*q) for a attempts, s students, q quizzes.
    """
    row_of = _positions(student_ids, "student")
    col_of = _positions(quiz_ids, "quiz")
    latest = _latest_scores(attempts)
    unknown = [pair for pair in latest
               if pair[0] not in row_of or pair[1] not in col_of]
    if unknown:
        raise ValidationError(f"Attempt for unknown student or quiz: {unknown[0]}")
    matrix = np.full((len(student_ids), len(quiz_ids)), np.nan)
    if latest:
        rows = np.array([row_of[student] for student, _ in latest])
        cols = np.array([col_of[quiz] for _, quiz in latest])
        matrix[rows, cols] = np.array(list(latest.values()))
    return matrix


def _as_matrix(matrix):
    """Turn the input into a 2-D float array, or explain why not.

    Args:
        matrix: anything np.asarray accepts (array, nested lists).
    Returns:
        2-D float numpy array.
    Raises:
        ValidationError: if the values are not numbers or it is not 2-D.
    Complexity: O(s*q).
    """
    try:
        array = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"The score matrix must hold numbers: {error}") from error
    if array.ndim != 2:
        raise ValidationError(f"The score matrix must be 2-D, not {array.ndim}-D.")
    return array


def to_percentages(matrix, max_scores):
    """Convert raw scores to percentages by broadcasting.

    max_scores has shape (q,), the matrix (s, q), so NumPy stretches the
    max scores down every row: each column is divided by its own quiz's max.

    Args:
        matrix: (s, q) array of raw scores.
        max_scores: length-q array of each quiz's max score.
    Returns:
        (s, q) array: matrix / max_scores * 100 (NaN stays NaN).
    Raises:
        ValidationError: shapes do not match or a max score is <= 0.
    Complexity: O(s*q), vectorised.
    """
    matrix = _as_matrix(matrix)
    try:
        maxima = np.asarray(max_scores, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"Max scores must be numbers: {error}") from error
    if maxima.shape != (matrix.shape[1],):
        raise ValidationError(
            f"Need {matrix.shape[1]} max scores, got shape {maxima.shape}.")
    if not np.all(maxima > 0):     # also catches NaN, since NaN > 0 is False
        raise ValidationError("Every max score must be greater than 0.")
    return matrix / maxima * 100


def missing_mask(matrix):
    """Find the missing attempts.

    Args:
        matrix: (s, q) array.
    Returns:
        boolean (s, q) array, True where the value is NaN.
    Raises:
        ValidationError: if the matrix is not a 2-D array of numbers.
    Complexity: O(s*q), vectorised.
    """
    return np.isnan(_as_matrix(matrix))


def _nan_mean(matrix, axis: int):
    """Mean along one axis, skipping NaN (like np.nanmean).

    Sum of the real values / how many real values. A row or column with no
    real values gives NaN instead of np.nanmean's "Mean of empty slice"
    warning.

    Args:
        matrix: (s, q) array.
        axis: 0 for each column (quiz), 1 for each row (student).
    Returns:
        1-D array of means.
    Raises:
        ValidationError: if the matrix is not a 2-D array of numbers.
    Complexity: O(s*q), vectorised.
    """
    matrix = _as_matrix(matrix)
    present = ~missing_mask(matrix)                  # True = real attempt
    totals = np.where(present, matrix, 0.0).sum(axis=axis)
    counts = present.sum(axis=axis)
    means = np.full(totals.shape, np.nan)
    np.divide(totals, counts, out=means, where=counts > 0)
    return means


def quiz_averages(matrix):
    """Average of each quiz (column), ignoring missing attempts.

    Args:
        matrix: (s, q) array.
    Returns:
        length-q array (same as np.nanmean along axis=0; NaN for a quiz that
        nobody took).
    Raises:
        ValidationError: if the matrix is not a 2-D array of numbers.
    Complexity: O(s*q), vectorised.
    """
    return _nan_mean(matrix, axis=0)


def student_averages(matrix):
    """Average of each student (row), ignoring missing attempts.

    Args:
        matrix: (s, q) array.
    Returns:
        length-s array (same as np.nanmean along axis=1; NaN for a student
        who took no quiz).
    Raises:
        ValidationError: if the matrix is not a 2-D array of numbers.
    Complexity: O(s*q), vectorised.
    """
    return _nan_mean(matrix, axis=1)


def _loop_percent_mean(scores: list[float], max_score: float) -> float:
    """Average percentage the slow way, one element at a time.

    Args:
        scores: raw scores as a plain Python list.
        max_score: the maximum possible score.
    Returns:
        mean percentage.
    Complexity: O(n) Python steps (slow on purpose, for the comparison).
    """
    total = 0.0
    for score in scores:
        total += score / max_score * 100
    return total / len(scores)


def loop_vs_vector_demo(size: int = 100_000) -> tuple[float, float]:
    """Time a Python loop against the vectorised version (Lab 07 comparison).

    Both versions compute the mean percentage of the same random scores
    (0..10 out of 10), and they must agree.

    Args:
        size: number of random scores to use.
    Returns:
        (loop_seconds, vector_seconds).
    Raises:
        ValidationError: if size is not a whole number >= 1.
    Complexity: O(size).
    """
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValidationError("size must be a whole number of at least 1.")
    scores = np.random.default_rng(42).integers(0, 11, size).astype(float)
    as_list = scores.tolist()
    start = time.perf_counter()
    loop_mean = _loop_percent_mean(as_list, 10.0)
    loop_seconds = time.perf_counter() - start
    start = time.perf_counter()
    vector_mean = (scores / 10.0 * 100).mean()
    vector_seconds = time.perf_counter() - start
    assert np.isclose(loop_mean, vector_mean), "loop and vector results differ"
    return loop_seconds, vector_seconds


def _cell(value: float) -> str:
    """Format one number for the table ("-" for a missing attempt).

    Args:
        value: a score, percentage or NaN.
    Returns:
        text 6 characters wide.
    Complexity: O(1).
    """
    return f"{'-':>6}" if np.isnan(value) else f"{value:6.1f}"


def print_course_table(store, course) -> None:
    """Print the percentage matrix of one course with its averages.

    Args:
        store: the loaded DataStore (quizzes and attempts).
        course: the Course whose enrolled students and quizzes are shown.
    Raises:
        ValidationError: if the attempts refer to an unknown student or quiz.
    Complexity: O(a log a + s*q).
    """
    student_ids = sorted(course.enrolled)
    quizzes = sorted((quiz for quiz in store.quizzes.values()
                      if quiz.course_id == course.course_id),
                     key=lambda quiz: quiz.quiz_id)
    quiz_ids = [quiz.quiz_id for quiz in quizzes]
    wanted = [record for record in store.attempts
              if record["student_id"] in course.enrolled
              and record["quiz_id"] in quiz_ids]
    percent = to_percentages(score_matrix(wanted, student_ids, quiz_ids),
                             [quiz.max_score for quiz in quizzes])
    print(f"\n{course.course_id} {course.title} (percent, '-' = not attempted)")
    print("Student" + "".join(f"{quiz_id:>6}" for quiz_id in quiz_ids) + "   Avg")
    for student_id, row, avg in zip(student_ids, percent, student_averages(percent)):
        print(f"{student_id:<7}" + "".join(_cell(v) for v in row) + _cell(avg))
    print("Avg    " + "".join(_cell(v) for v in quiz_averages(percent)))
    print(f"Missing attempts: {int(missing_mask(percent).sum())}")


if __name__ == "__main__":
    from storage import DataStore
    try:
        lms = DataStore()
        lms.load()
        for lms_course in lms.courses.values():
            print_course_table(lms, lms_course)
        loop_s, vector_s = loop_vs_vector_demo()
        print(f"\n100,000 scores: loop {loop_s * 1000:.2f} ms, "
              f"vectorised {vector_s * 1000:.2f} ms "
              f"({loop_s / max(vector_s, 1e-9):.0f}x faster)")
    except LMSError as error:
        print(f"Could not build the score table: {error}")
