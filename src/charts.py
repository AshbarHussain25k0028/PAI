"""Labelled progress charts saved as PNG files.

Owner: Ashbar Hussain (Part 13)
Lab concepts: Lab 09 (Matplotlib line, bar and histogram; Seaborn heatmap).

Every chart has a title, axis labels and a legend where needed, and is
saved to outputs/figures/. Charts are saved, not shown, so the console
program never blocks on a window.

INTERFACE STUB (Part 1): bodies are written in Part 13.
"""

from __future__ import annotations

from pathlib import Path

FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"


def quiz_average_line(progress, path=None) -> Path:
    """Line chart of the class average for each quiz, in date order.

    Args:
        progress: cleaned progress DataFrame (analysis.py).
        path: where to save; defaults to FIGURES_DIR/quiz_averages.png.
    Returns:
        the Path of the saved PNG.
    Raises:
        ValidationError: if progress is empty.
    Complexity: O(n) for n rows.
    """
    raise NotImplementedError("Part 13")


def completion_bar(submissions, students_per_course: dict, path=None) -> Path:
    """Bar chart of how many students submitted each assignment.

    Args:
        submissions: cleaned submission DataFrame.
        students_per_course: {course_id: number of enrolled students}.
        path: where to save; defaults to FIGURES_DIR/assignment_completion.png.
    Returns:
        the Path of the saved PNG.
    Raises:
        ValidationError: if there are no assignments.
    Complexity: O(n) for n rows.
    """
    raise NotImplementedError("Part 13")


def score_histogram(percentages, path=None) -> Path:
    """Histogram of quiz score percentages.

    Args:
        percentages: array or Series of percentages (NaN is skipped).
        path: where to save; defaults to FIGURES_DIR/score_histogram.png.
    Returns:
        the Path of the saved PNG.
    Raises:
        ValidationError: if there are no values.
    Complexity: O(n) for n values.
    """
    raise NotImplementedError("Part 13")


def topic_heatmap(topic_table, path=None) -> Path:
    """Optional Seaborn heatmap of percent correct (rows: course, cols: topic).

    Args:
        topic_table: DataFrame from analysis.topic_summary().
        path: where to save; defaults to FIGURES_DIR/topic_heatmap.png.
    Returns:
        the Path of the saved PNG.
    Raises:
        ValidationError: if topic_table is empty.
    Complexity: O(c*t) for c courses and t topics.
    """
    raise NotImplementedError("Part 13")
