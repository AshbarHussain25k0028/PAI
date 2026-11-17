"""Labelled progress charts saved as PNG files.

Owner: Ashbar Hussain (Part 13)
Lab concepts: Lab 09 (Matplotlib line, bar and histogram; Seaborn heatmap).

Every chart has a title, axis labels and a legend where needed, and is
saved to outputs/figures/. Charts are saved, not shown, so the console
program never blocks on a window (the non-interactive "Agg" backend is used).

Key data structure
------------------
The charts read the Pandas tables built in analysis.py. A dict
{course_id: enrolled count} is used to turn "number submitted" into a
completion percentage.

Run `python src/charts.py` to save all four charts for the loaded data.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")   # draw to files only, no window
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from exceptions import LMSError, ValidationError  # noqa: E402

FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"
PASS_MARK = 60.0   # percent, same pass mark as analysis.py


def _save(figure, path, default_name: str) -> Path:
    """Save a figure as a PNG and close it.

    Args:
        figure: the Matplotlib figure.
        path: target path, or None to use FIGURES_DIR/default_name.
        default_name: file name used when path is None.
    Returns:
        the Path of the saved PNG.
    Complexity: O(1) in the data size (drawing cost only).
    """
    target = Path(path) if path is not None else FIGURES_DIR / default_name
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(target, dpi=150)
    plt.close(figure)
    return target


def _require_rows(table, what: str) -> None:
    """Raise ValidationError unless table is a non-empty DataFrame.

    Args:
        table: value to check.
        what: name used in the error message.
    Raises:
        ValidationError: if table is not a DataFrame or has no rows.
    Complexity: O(1).
    """
    if not isinstance(table, pd.DataFrame) or table.empty:
        raise ValidationError(f"No {what} to draw a chart from.")


def quiz_average_line(progress, path=None) -> Path:
    """Line chart of the class average for each quiz, in date order.

    One line per course, one point per quiz. The x position is the date of
    the quiz's first attempt, and a dashed line marks the pass mark.

    Args:
        progress: cleaned progress DataFrame (analysis.py).
        path: where to save; defaults to FIGURES_DIR/quiz_averages.png.
    Returns:
        the Path of the saved PNG.
    Raises:
        ValidationError: if progress is empty.
    Complexity: O(n) for n rows.
    """
    _require_rows(progress, "quiz attempts")
    quizzes = progress.groupby(["course_id", "quiz_id"], as_index=False).agg(
        average=("percent", "mean"), when=("attempted_on", "min"))
    figure, axis = plt.subplots(figsize=(8, 5))
    for course_id, rows in quizzes.groupby("course_id"):
        rows = rows.sort_values("when")
        axis.plot(rows["when"], rows["average"], marker="o", label=str(course_id))
    axis.axhline(PASS_MARK, linestyle="--", color="gray", label="Pass mark")
    axis.set(title="Class average per quiz", xlabel="Date of quiz",
             ylabel="Average score (%)", ylim=(0, 100))
    axis.legend(title="Course")
    figure.autofmt_xdate()
    return _save(figure, path, "quiz_averages.png")


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
    _require_rows(submissions, "submissions")
    counts = submissions.groupby(["course_id", "assignment_id"]).size()
    counts = counts.reset_index(name="submitted")
    counts["enrolled"] = counts["course_id"].map(students_per_course).fillna(0)
    figure, axis = plt.subplots(figsize=(8, 5))
    positions = np.arange(len(counts))
    axis.bar(positions - 0.2, counts["enrolled"], width=0.4, color="lightgray",
             label="Enrolled students")
    axis.bar(positions + 0.2, counts["submitted"], width=0.4, label="Submitted")
    axis.set_xticks(positions)
    axis.set_xticklabels(counts["assignment_id"])
    axis.set(title="Assignment completion", xlabel="Assignment",
             ylabel="Number of students")
    axis.legend()
    return _save(figure, path, "assignment_completion.png")


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
    values = np.asarray(percentages, dtype=float).ravel()
    values = values[~np.isnan(values)]
    if values.size == 0:
        raise ValidationError("No scores to draw a histogram from.")
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.hist(values, bins=np.arange(0, 110, 10), edgecolor="black",
              label=f"Attempts (n={values.size})")
    axis.axvline(values.mean(), color="red", linestyle="--",
                 label=f"Mean {values.mean():.1f}%")
    axis.set(title="Distribution of quiz scores", xlabel="Score (%)",
             ylabel="Number of attempts")
    axis.legend()
    return _save(figure, path, "score_histogram.png")


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
    _require_rows(topic_table, "topic results")
    grid = topic_table.pivot(index="course_id", columns="topic", values="percent")
    figure, axis = plt.subplots(figsize=(8, 4))
    sns.heatmap(grid, annot=True, fmt=".0f", vmin=0, vmax=100, cmap="YlGnBu",
                linewidths=0.5, cbar_kws={"label": "Correct (%)"}, ax=axis)
    axis.set(title="Percent correct by course and topic", xlabel="Topic",
             ylabel="Course")
    return _save(figure, path, "topic_heatmap.png")


def make_all_charts(store, folder=None) -> list:
    """Save all four charts for the loaded data.

    Args:
        store: the loaded DataStore.
        folder: output folder; defaults to FIGURES_DIR.
    Returns:
        list of the saved Paths.
    Raises:
        ValidationError: if there is no data for a chart.
    Complexity: O(a * k + s) for a attempts of k questions, s submissions.
    """
    from analysis import frames_from_store, topic_summary
    folder = Path(folder) if folder is not None else FIGURES_DIR
    progress, submissions = frames_from_store(store)
    sizes = {c.course_id: len(c.enrolled) for c in store.courses.values()}
    return [
        quiz_average_line(progress, folder / "quiz_averages.png"),
        completion_bar(submissions, sizes, folder / "assignment_completion.png"),
        score_histogram(progress["percent"], folder / "score_histogram.png"),
        topic_heatmap(topic_summary(store.attempts, store.quizzes),
                      folder / "topic_heatmap.png"),
    ]


if __name__ == "__main__":
    from storage import DataStore
    try:
        lms = DataStore()
        lms.load()
        for saved in make_all_charts(lms):
            print(f"Saved {saved}")
    except LMSError as error:
        print(f"Could not draw the charts: {error}")
