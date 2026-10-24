"""Quiz scores as a NumPy matrix (students x quizzes).

Owner: Muhammad Mudassir (Part 10)
Lab concepts: Lab 07 (2-D arrays, boolean masks, NaN, broadcasting,
mean along an axis, vectorisation instead of loops).

Key data structure
------------------
A 2-D float array: one row per student, one column per quiz.
A missing attempt is NaN, so it is not counted as a zero.
All maths on the matrix is vectorised: no Python loop over the elements.

INTERFACE STUB (Part 1): bodies are written in Part 10.
"""

from __future__ import annotations


def score_matrix(attempts: list[dict], student_ids: list[str],
                 quiz_ids: list[str]):
    """Build the students x quizzes score matrix.

    Args:
        attempts: records from attempts.json.
        student_ids: row order.
        quiz_ids: column order.
    Returns:
        numpy array of shape (len(student_ids), len(quiz_ids)); NaN where a
        student has no attempt (the latest attempt wins if there are two).
    Raises:
        ValidationError: if an attempt has an unknown student or quiz.
    Complexity: O(a + s*q) for a attempts, s students, q quizzes.
    """
    raise NotImplementedError("Part 10")


def to_percentages(matrix, max_scores):
    """Convert raw scores to percentages by broadcasting.

    Args:
        matrix: (s, q) array of raw scores.
        max_scores: length-q array of each quiz's max score.
    Returns:
        (s, q) array: matrix / max_scores * 100 (NaN stays NaN).
    Raises:
        ValidationError: shapes do not match or a max score is <= 0.
    Complexity: O(s*q), vectorised.
    """
    raise NotImplementedError("Part 10")


def missing_mask(matrix):
    """Find the missing attempts.

    Args:
        matrix: (s, q) array.
    Returns:
        boolean (s, q) array, True where the value is NaN.
    Complexity: O(s*q), vectorised.
    """
    raise NotImplementedError("Part 10")


def quiz_averages(matrix):
    """Average of each quiz (column), ignoring missing attempts.

    Args:
        matrix: (s, q) array.
    Returns:
        length-q array (np.nanmean along axis=0).
    Complexity: O(s*q), vectorised.
    """
    raise NotImplementedError("Part 10")


def student_averages(matrix):
    """Average of each student (row), ignoring missing attempts.

    Args:
        matrix: (s, q) array.
    Returns:
        length-s array (np.nanmean along axis=1).
    Complexity: O(s*q), vectorised.
    """
    raise NotImplementedError("Part 10")


def loop_vs_vector_demo(size: int = 100_000) -> tuple[float, float]:
    """Time a Python loop against the vectorised version (Lab 07 comparison).

    Args:
        size: number of random scores to use.
    Returns:
        (loop_seconds, vector_seconds).
    Raises:
        ValidationError: if size < 1.
    Complexity: O(size).
    """
    raise NotImplementedError("Part 10")
