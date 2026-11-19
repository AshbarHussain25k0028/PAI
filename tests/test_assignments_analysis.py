"""Edge-case tests for assignments.py and analysis.py.

Owner: Ashbar Hussain (Part 15)
Cases: empty input, one element, duplicates, large input, invalid input.
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from analysis import (build_progress_frame, build_submission_frame,
                      class_report, clean_frame, course_summary,
                      latest_only, needs_attention, topic_summary)
from assignments import (Assignment, Submission, pending_for_student,
                         submit_work)
from exceptions import (DuplicateError, NotFoundError, ValidationError)
from quizzes import Quiz, make_question

DEADLINE = datetime(2026, 11, 10, 23, 59)


def make_assignment(aid="AS01", course="C1", max_marks=10):
    """A small valid Assignment."""
    return Assignment(aid, course, "Gradebook", DEADLINE, max_marks)


def make_quiz(quiz_id="Q1", course="C1", answers=(0, 1)):
    """A quiz with one question per answer index, topics a and b."""
    quiz = Quiz(quiz_id, course, "Quiz")
    for number, answer in enumerate(answers):
        topic = "a" if number % 2 == 0 else "b"
        quiz.add_question(make_question(f"{quiz_id}-{number}", "Question?",
                                        ["w", "x", "y", "z"], answer, topic))
    return quiz


# ---------- Assignment ----------

@pytest.mark.parametrize("args", [
    ("", "C1", "T", DEADLINE, 10), ("AS1", "", "T", DEADLINE, 10),
    ("AS1", "C1", "  ", DEADLINE, 10), ("AS1", "C1", "T", "2026-11-10", 10),
    ("AS1", "C1", "T", None, 10), ("AS1", "C1", "T", DEADLINE, 0),
    ("AS1", "C1", "T", DEADLINE, -5), ("AS1", "C1", "T", DEADLINE, True),
    ("AS1", "C1", "T", DEADLINE, 2.5), ("AS1", "C1", "T", DEADLINE, "ten"),
    ("AS1", "C1", "T", DEADLINE, None),
])
def test_assignment_rejects_invalid(args):
    """Bad IDs, titles, dates or maximum marks raise ValidationError."""
    with pytest.raises(ValidationError):
        Assignment(*args)


def test_assignment_accepts_digit_text_max_marks():
    """max_marks "10" (from a file) becomes the int 10."""
    assert make_assignment(max_marks="10").max_marks == 10


def test_assignment_is_open_at_exact_deadline():
    """The deadline moment itself is still open; one minute later is closed."""
    assignment = make_assignment()
    assert assignment.is_open(DEADLINE)
    assert not assignment.is_open(DEADLINE + timedelta(minutes=1))


def test_assignment_dict_round_trip():
    """to_dict and from_dict are inverse; deadline is stored as text."""
    assignment = make_assignment()
    record = assignment.to_dict()
    assert record["deadline"] == "2026-11-10 23:59"
    copy = Assignment.from_dict(record)
    assert copy.to_dict() == record


@pytest.mark.parametrize("record", [
    None, [], {}, {"assignment_id": "A"},
    {"assignment_id": "A", "course_id": "C", "title": "T",
     "deadline": "tomorrow", "max_marks": 10},
    {"assignment_id": "A", "course_id": "C", "title": "T",
     "deadline": "2026-02-30 10:00", "max_marks": 10},
    {"assignment_id": "A", "course_id": "C", "title": "T",
     "deadline": "2026-11-10 23:59", "max_marks": 0},
])
def test_assignment_from_dict_invalid(record):
    """Missing fields, bad dates (even 30 Feb) and bad marks are refused."""
    with pytest.raises(ValidationError):
        Assignment.from_dict(record)


# ---------- Submission and marks ----------

def make_submission(max_marks=10, when=DEADLINE):
    """A valid unmarked Submission."""
    return Submission("S01", "AS01", when, "my answer", max_marks)


def test_new_submission_is_unmarked():
    """A new submission has marks None and an empty feedback."""
    sub = make_submission()
    assert sub.marks is None and sub.feedback == ""
    assert sub.key == ("S01", "AS01")


@pytest.mark.parametrize("mark", [0, 1, 10, "7", " 5 "])
def test_marks_accepts_valid_values(mark):
    """Boundaries 0 and max, and digit text, are accepted."""
    sub = make_submission()
    sub.marks = mark
    assert sub.marks == int(mark)


@pytest.mark.parametrize("mark", [-1, 11, 1000, True, 2.5, "x", "", None, "1.5"])
def test_marks_rejects_invalid_values_and_keeps_old(mark):
    """Out-of-range or non-integer marks are refused and the old mark stays."""
    sub = make_submission()
    sub.marks = 4
    with pytest.raises(ValidationError):
        sub.marks = mark
    assert sub.marks == 4


@pytest.mark.parametrize("args", [
    ("", "AS01", DEADLINE, "t", 10), ("S01", "", DEADLINE, "t", 10),
    ("S01", "AS01", "2026-11-10", "t", 10), ("S01", "AS01", DEADLINE, "", 10),
    ("S01", "AS01", DEADLINE, "   ", 10), ("S01", "AS01", DEADLINE, "t", 0),
])
def test_submission_rejects_invalid(args):
    """Empty IDs/text, a non-datetime and max_marks 0 raise ValidationError."""
    with pytest.raises(ValidationError):
        Submission(*args)


def test_is_late_boundaries():
    """On the deadline is on time; one minute after is late."""
    assignment = make_assignment()
    assert not make_submission(when=DEADLINE).is_late(assignment)
    assert make_submission(
        when=DEADLINE + timedelta(minutes=1)).is_late(assignment)
    assert not make_submission(
        when=DEADLINE - timedelta(days=30)).is_late(assignment)


def test_submission_from_dict_blank_and_given_marks():
    """A blank marks column means unmarked; a value is checked by the setter."""
    row = {"student_id": "S01", "assignment_id": "AS01",
           "submitted_at": "2026-11-09 10:00", "text": "t",
           "marks": "", "feedback": " good "}
    assert Submission.from_dict(row, 10).marks is None
    assert Submission.from_dict(row, 10).feedback == "good"
    row["marks"] = "8"
    assert Submission.from_dict(row, 10).marks == 8
    row["marks"] = "11"
    with pytest.raises(ValidationError):
        Submission.from_dict(row, 10)


@pytest.mark.parametrize("change", [
    {"submitted_at": "bad"}, {"submitted_at": ""}, {"text": ""},
    {"marks": "abc"}, {"student_id": ""},
])
def test_submission_from_dict_invalid(change):
    """Bad dates, empty text, non-numeric marks or empty IDs are refused."""
    row = {"student_id": "S01", "assignment_id": "AS01",
           "submitted_at": "2026-11-09 10:00", "text": "t",
           "marks": "", "feedback": ""}
    row.update(change)
    with pytest.raises(ValidationError):
        Submission.from_dict(row, 10)


def test_submission_from_dict_not_a_dict():
    """A non-dict row raises ValidationError."""
    with pytest.raises(ValidationError):
        Submission.from_dict(None, 10)


def test_submission_dict_round_trip():
    """to_dict then from_dict keeps marks and feedback; unmarked stays blank."""
    sub = make_submission()
    assert sub.to_dict()["marks"] == ""
    sub.marks = 0
    sub.feedback = "ok"
    row = sub.to_dict()
    assert row["marks"] == 0
    copy = Submission.from_dict({k: str(v) for k, v in row.items()}, 10)
    assert copy.marks == 0 and copy.feedback == "ok"


# ---------- submit_work and pending_for_student ----------

def test_submit_work_stores_under_tuple_key():
    """A submission lands in the dict under (student, assignment)."""
    submissions = {}
    sub = submit_work(submissions, make_assignment(), "S01", "text", DEADLINE)
    assert submissions == {("S01", "AS01"): sub}


def test_submit_work_duplicate_is_refused():
    """A second submission by the same student raises DuplicateError."""
    submissions = {}
    assignment = make_assignment()
    submit_work(submissions, assignment, "S01", "first", DEADLINE)
    with pytest.raises(DuplicateError):
        submit_work(submissions, assignment, "S01", "second", DEADLINE)
    assert submissions[("S01", "AS01")].text == "first"
    assert len(submissions) == 1


def test_submit_work_empty_text_not_stored():
    """Empty text raises ValidationError and nothing is stored."""
    submissions = {}
    with pytest.raises(ValidationError):
        submit_work(submissions, make_assignment(), "S01", "  ", DEADLINE)
    assert submissions == {}


def test_submit_late_is_accepted_and_flagged():
    """Late work is stored, and is_late reports it."""
    submissions = {}
    assignment = make_assignment()
    late = DEADLINE + timedelta(days=3)
    sub = submit_work(submissions, assignment, "S01", "late", late)
    assert sub.is_late(assignment)


def test_pending_empty_inputs():
    """No assignments, or no courses, gives an empty list."""
    assert pending_for_student({}, {}, "S01", {"C1"}) == []
    assert pending_for_student({"AS01": make_assignment()}, {}, "S01",
                               set()) == []


def test_pending_single_and_submitted():
    """One open assignment is pending until the student submits it."""
    assignment = make_assignment()
    assignments = {"AS01": assignment}
    assert pending_for_student(assignments, {}, "S01", {"C1"}) == [assignment]
    submissions = {}
    submit_work(submissions, assignment, "S01", "done", DEADLINE)
    assert pending_for_student(assignments, submissions, "S01", {"C1"}) == []
    assert pending_for_student(assignments, submissions, "S02", {"C1"}) == \
        [assignment]


def test_pending_sorted_by_deadline_and_filtered_by_course():
    """Earliest deadline first; other courses are left out."""
    late = Assignment("AS02", "C1", "Late", DEADLINE + timedelta(days=5), 10)
    early = Assignment("AS03", "C1", "Early", DEADLINE - timedelta(days=5), 10)
    other = Assignment("AS04", "C2", "Other", DEADLINE, 10)
    assignments = {a.assignment_id: a for a in (late, other, early)}
    result = pending_for_student(assignments, {}, "S01", {"C1"})
    assert [a.assignment_id for a in result] == ["AS03", "AS02"]


def test_pending_large_input():
    """5,000 assignments are sorted correctly."""
    assignments = {}
    for i in range(5000):
        aid = f"AS{i}"
        assignments[aid] = Assignment(aid, "C1", "T",
                                      DEADLINE - timedelta(minutes=i), 10)
    result = pending_for_student(assignments, {}, "S01", {"C1"})
    assert len(result) == 5000
    assert result[0].assignment_id == "AS4999"


def test_large_submission_dict():
    """10,000 different students can submit the same assignment."""
    submissions = {}
    assignment = make_assignment()
    for i in range(10000):
        submit_work(submissions, assignment, f"S{i}", "x", DEADLINE)
    assert len(submissions) == 10000
    with pytest.raises(DuplicateError):
        submit_work(submissions, assignment, "S5", "again", DEADLINE)


# ---------- analysis: frames ----------

def attempt(student="S01", quiz="Q1", when="2026-11-01 10:00", score=1,
            maximum=2, answers=(0, 0)):
    """One attempts.json record."""
    return {"attempt_id": "AT", "student_id": student, "quiz_id": quiz,
            "attempted_on": when, "answers": list(answers),
            "score": score, "max_score": maximum}


def test_progress_frame_empty_input():
    """No attempts gives an empty frame that still has the columns."""
    frame = build_progress_frame([], {"Q1": make_quiz()})
    assert frame.empty
    assert "percent" in frame.columns and "course_id" in frame.columns


def test_progress_frame_single_attempt():
    """One attempt gets its course and percent."""
    frame = build_progress_frame([attempt(score=1, maximum=2)],
                                 {"Q1": make_quiz()})
    assert len(frame) == 1
    assert frame.loc[0, "course_id"] == "C1"
    assert frame.loc[0, "percent"] == 50.0


@pytest.mark.parametrize("bad", ["text", None, {"a": 1}, 5])
def test_progress_frame_rejects_non_list(bad):
    """attempts must be a list."""
    with pytest.raises(ValidationError):
        build_progress_frame(bad, {})


def test_progress_frame_unknown_quiz():
    """An attempt at an unknown quiz is refused and named in the message."""
    with pytest.raises(ValidationError, match="Q9"):
        build_progress_frame([attempt(quiz="Q9")], {"Q1": make_quiz()})


def test_progress_frame_zero_max_score_is_not_a_crash():
    """max_score 0 gives a non-finite percent instead of an exception."""
    frame = build_progress_frame([attempt(score=0, maximum=0)],
                                 {"Q1": make_quiz()})
    assert len(frame) == 1


def test_submission_frame_empty_and_invalid():
    """Empty input is fine; a non-list or unknown assignment is refused."""
    assert build_submission_frame([], {"AS01": make_assignment()}).empty
    with pytest.raises(ValidationError):
        build_submission_frame("rows", {})
    row = {"student_id": "S01", "assignment_id": "AS99",
           "submitted_at": "2026-11-09 10:00", "marks": "5"}
    with pytest.raises(ValidationError, match="AS99"):
        build_submission_frame([row], {"AS01": make_assignment()})


def sub_row(student="S01", aid="AS01", when="2026-11-09 10:00", marks="5"):
    """One submissions.csv-style row."""
    return {"student_id": student, "assignment_id": aid,
            "submitted_at": when, "marks": marks}


def test_submission_frame_late_flag_and_blank_marks():
    """Late flag compares with the deadline; blank marks become NaN."""
    rows = [sub_row("S01", when="2026-11-09 10:00", marks=""),
            sub_row("S02", when="2026-11-11 08:00", marks="8")]
    frame = clean_frame(build_submission_frame(
        rows, {"AS01": make_assignment()}))
    by_student = frame.set_index("student_id")
    assert not by_student.loc["S01", "late"]
    assert by_student.loc["S02", "late"]
    assert pd.isna(by_student.loc["S01", "marks"])
    assert by_student.loc["S02", "percent"] == 80.0


# ---------- analysis: cleaning ----------

def test_clean_frame_rejects_non_frame():
    """Only DataFrames are cleaned."""
    with pytest.raises(ValidationError):
        clean_frame([1, 2])


def test_clean_frame_empty_frame():
    """An empty progress frame cleans to an empty frame."""
    frame = build_progress_frame([], {"Q1": make_quiz()})
    assert clean_frame(frame).empty


def test_clean_frame_drops_exact_duplicates_and_blank_students():
    """Duplicate rows and rows without a student are removed; IDs tidy up."""
    rows = [attempt(student=" s01 "), attempt(student="S01"),
            attempt(student=""), attempt(student="S02")]
    frame = clean_frame(build_progress_frame(rows, {"Q1": make_quiz()}))
    assert sorted(frame["student_id"]) == ["S01", "S02"]


def test_clean_frame_does_not_change_input():
    """The original frame is left untouched."""
    frame = build_progress_frame([attempt(student=" s01 ")],
                                 {"Q1": make_quiz()})
    clean_frame(frame)
    assert frame.loc[0, "student_id"] == " s01 "


def test_clean_frame_bad_numbers_and_dates_become_missing():
    """Unreadable score and date values become NaN/NaT, not crashes."""
    frame = build_progress_frame(
        [attempt(when="not a date", score="abc")], {"Q1": make_quiz()})
    cleaned = clean_frame(frame)
    assert pd.isna(cleaned.loc[0, "score"])
    assert pd.isna(cleaned.loc[0, "attempted_on"])
    assert pd.isna(cleaned.loc[0, "percent"])


# ---------- analysis: latest, summary, report ----------

def progress_from(rows, quizzes=None):
    """Cleaned progress frame from attempt records."""
    quizzes = quizzes or {"Q1": make_quiz()}
    return clean_frame(build_progress_frame(rows, quizzes))


def test_latest_only_keeps_newest_attempt():
    """Of two attempts at the same quiz, only the newer one stays."""
    rows = [attempt(when="2026-11-02 10:00", score=2),
            attempt(when="2026-11-01 10:00", score=0)]
    latest = latest_only(progress_from(rows))
    assert len(latest) == 1 and latest.iloc[0]["score"] == 2


def test_latest_only_empty():
    """An empty frame stays empty."""
    assert latest_only(progress_from([])).empty


def test_course_summary_empty_and_single():
    """Empty gives no rows; one attempt gives its percent and count."""
    assert course_summary(progress_from([])).empty
    summary = course_summary(progress_from([attempt(score=1, maximum=2)]))
    assert summary.loc["C1", "mean_percent"] == 50.0
    assert summary.loc["C1", "attempts"] == 1


def test_course_summary_ignores_missing_percent():
    """A NaN percent is skipped by the mean but still counted as an attempt."""
    rows = [attempt(student="S01", score=2), attempt(student="S02", score="x")]
    summary = course_summary(progress_from(rows))
    assert summary.loc["C1", "mean_percent"] == 100.0
    assert summary.loc["C1", "attempts"] == 2


def test_topic_summary_empty_and_unknown_quiz():
    """No attempts gives an empty table; an unknown quiz is refused."""
    assert topic_summary([], {"Q1": make_quiz()}).empty
    with pytest.raises(ValidationError):
        topic_summary([attempt(quiz="Q9")], {"Q1": make_quiz()})


def test_topic_summary_counts_latest_attempt_only():
    """Only the newest attempt is counted per student and quiz."""
    rows = [attempt(when="2026-11-01 10:00", answers=(3, 3)),
            attempt(when="2026-11-02 10:00", answers=(0, 1))]
    table = topic_summary(rows, {"Q1": make_quiz()})
    assert set(table["percent"]) == {100.0}
    assert set(table["topic"]) == {"a", "b"}


def test_topic_summary_wrong_answer_count():
    """Answers that do not fit the quiz raise ValidationError."""
    with pytest.raises(ValidationError):
        topic_summary([attempt(answers=(0,))], {"Q1": make_quiz()})


def test_class_report_unknown_course():
    """A course with no records raises NotFoundError."""
    progress = progress_from([attempt()])
    submissions = clean_frame(build_submission_frame(
        [], {"AS01": make_assignment()}))
    with pytest.raises(NotFoundError):
        class_report(progress, submissions, "C9")


def test_class_report_empty_frames():
    """Nothing at all also raises NotFoundError."""
    progress = progress_from([])
    submissions = clean_frame(build_submission_frame(
        [], {"AS01": make_assignment()}))
    with pytest.raises(NotFoundError):
        class_report(progress, submissions, "C1")


def test_class_report_lists_enrolled_students_without_work():
    """enrolled students with no work show up with missing_work counted."""
    progress = progress_from([attempt(student="S01", score=2)])
    submissions = clean_frame(build_submission_frame(
        [sub_row("S01", marks="9")], {"AS01": make_assignment()}))
    report = class_report(progress, submissions, " c1 ",
                          enrolled={"S01", "S02"})
    rows = report.set_index("student_id")
    assert rows.loc["S01", "missing_work"] == 0
    assert rows.loc["S02", "missing_work"] == 2
    assert pd.isna(rows.loc["S02", "quiz_avg"])


def test_class_report_unmarked_work_is_not_zero():
    """An unmarked submission is NaN in the average, but not 'missing'."""
    progress = progress_from([attempt(student="S01", score=2)])
    submissions = clean_frame(build_submission_frame(
        [sub_row("S01", marks="")], {"AS01": make_assignment()}))
    report = class_report(progress, submissions, "C1")
    assert pd.isna(report.loc[0, "assignment_avg"])
    assert report.loc[0, "missing_work"] == 0


def test_class_report_duplicate_attempts_count_once():
    """Two attempts at one quiz are one quiz done, not two."""
    rows = [attempt(when="2026-11-01 10:00", score=0),
            attempt(when="2026-11-02 10:00", score=2)]
    submissions = clean_frame(build_submission_frame(
        [], {"AS01": make_assignment()}))
    report = class_report(progress_from(rows), submissions, "C1")
    assert report.loc[0, "quiz_avg"] == 100.0
    assert report.loc[0, "missing_work"] == 0


def test_needs_attention_filters_and_sorts():
    """Weak or missing-work students are kept, weakest first."""
    report = pd.DataFrame({"student_id": ["S01", "S02", "S03", "S04"],
                           "quiz_avg": [90.0, 40.0, 20.0, 80.0],
                           "assignment_avg": [90.0, 90.0, 90.0, 90.0],
                           "missing_work": [0, 0, 0, 1]})
    result = needs_attention(report)
    assert list(result["student_id"]) == ["S03", "S02", "S04"]


def test_needs_attention_empty_and_all_fine():
    """An empty report or a strong class gives no rows."""
    empty = pd.DataFrame({"student_id": [], "quiz_avg": [],
                          "assignment_avg": [], "missing_work": []})
    assert needs_attention(empty).empty
    strong = pd.DataFrame({"student_id": ["S01"], "quiz_avg": [95.0],
                           "assignment_avg": [95.0], "missing_work": [0]})
    assert needs_attention(strong).empty


@pytest.mark.parametrize("mark", [-1, 101, "60", None, True, [60]])
def test_needs_attention_invalid_pass_mark(mark):
    """The pass mark must be a number from 0 to 100."""
    report = pd.DataFrame({"student_id": ["S01"], "quiz_avg": [50.0],
                           "assignment_avg": [50.0], "missing_work": [0]})
    with pytest.raises(ValidationError):
        needs_attention(report, mark)


def test_needs_attention_pass_mark_boundaries():
    """0 and 100 are valid; exactly the pass mark is not 'below' it."""
    report = pd.DataFrame({"student_id": ["S01"], "quiz_avg": [60.0],
                           "assignment_avg": [60.0], "missing_work": [0]})
    assert needs_attention(report, 60).empty
    assert len(needs_attention(report, 100)) == 1
    assert needs_attention(report, 0).empty


def test_large_report_10000_attempts():
    """10,000 attempts from 1,000 students build and summarise quickly."""
    quizzes = {f"Q{i}": make_quiz(f"Q{i}") for i in range(10)}
    rows = [attempt(student=f"S{i % 1000:04d}", quiz=f"Q{i % 10}",
                    when=f"2026-11-{1 + i % 28:02d} 10:00", score=i % 3,
                    maximum=2)
            for i in range(10000)]
    progress = clean_frame(build_progress_frame(rows, quizzes))
    submissions = clean_frame(build_submission_frame(
        [], {"AS01": make_assignment()}))
    report = class_report(progress, submissions, "C1")
    assert len(report) == 1000
    assert course_summary(progress).loc["C1", "attempts"] <= 10000
