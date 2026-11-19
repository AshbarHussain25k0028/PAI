"""Edge-case tests for courses.py and quizzes.py.

Owner: Muhammad Mudassir (Part 16)
Cases: empty input, one element, duplicates, large input, invalid input.
"""

import pytest

from courses import Course, Material
from exceptions import DuplicateError, NotFoundError, ValidationError
from quizzes import (Question, Quiz, make_question, merge_topic_results,
                     suggest_revision, weak_topics)


def _material(material_id="M01", course_id="C101", topic="oop"):
    """Build a valid Material."""
    return Material(material_id, course_id, "Notes", topic, "notes.txt")


def _quiz(count=3, topics=("oop", "files")):
    """Build a quiz of `count` questions whose right answer is always 1."""
    quiz = Quiz("Q01", "C101", "Test quiz")
    for number in range(count):
        quiz.add_question(make_question(f"Q{number}", f"Question {number}?",
                                        ["a", "b", "c", "d"], 1,
                                        topics[number % len(topics)]))
    return quiz


# ---------- Material and Course ----------

@pytest.mark.parametrize("bad", ["", "   ", None, 5])
def test_course_rejects_empty_or_non_text(bad):
    """Empty, blank or non-text values are refused."""
    with pytest.raises(ValidationError):
        Course(bad, "Title", "T01")
    with pytest.raises(ValidationError):
        Course("C101", bad, "T01")
    with pytest.raises(ValidationError):
        Course("C101", "Title", bad)


def test_new_course_is_empty():
    """A new course has no materials and no students."""
    course = Course("C101", "AI", "T01")
    assert course.materials == [] and course.enrolled == set()
    assert course.materials_for_topic("oop") == []


def test_material_topic_is_lower_case():
    """Topics are stored in lower case."""
    assert _material(topic=" OOP ").topic == "oop"


def test_enroll_one_student_and_duplicate():
    """The second enroll of the same student returns False."""
    course = Course("C101", "AI", "T01")
    assert course.enroll("S01") is True
    assert course.enroll(" S01 ") is False
    assert course.enrolled == {"S01"}
    assert course.is_enrolled("S01") and not course.is_enrolled("S02")


@pytest.mark.parametrize("bad", ["", "  ", None, 7])
def test_enroll_invalid_id(bad):
    """Invalid student IDs are refused and nothing is added."""
    course = Course("C101", "AI", "T01")
    with pytest.raises(ValidationError):
        course.enroll(bad)
    assert course.enrolled == set()


def test_unenroll():
    """A student can be removed once; removing again fails."""
    course = Course("C101", "AI", "T01")
    course.enroll("S01")
    course.unenroll("S01")
    assert not course.is_enrolled("S01")
    with pytest.raises(NotFoundError):
        course.unenroll("S01")


def test_enroll_many_students():
    """10,000 students, with every ID entered twice."""
    course = Course("C101", "AI", "T01")
    for number in range(10_000):
        course.enroll(f"S{number}")
    assert all(course.enroll(f"S{number}") is False for number in range(10_000))
    assert len(course.enrolled) == 10_000


def test_add_material_rules():
    """Wrong type, wrong course and duplicate IDs are refused."""
    course = Course("C101", "AI", "T01")
    course.add_material(_material("M01"))
    with pytest.raises(DuplicateError):
        course.add_material(_material("M01"))
    with pytest.raises(ValidationError):
        course.add_material(_material("M02", course_id="C102"))
    with pytest.raises(ValidationError):
        course.add_material("not a material")
    assert [m.material_id for m in course.materials] == ["M01"]


def test_materials_keep_order_and_filter_by_topic():
    """Order is kept; topic search ignores case and spaces."""
    course = Course("C101", "AI", "T01")
    for number, topic in enumerate(["oop", "files", "oop"], start=1):
        course.add_material(_material(f"M{number}", topic=topic))
    assert [m.material_id for m in course.materials] == ["M1", "M2", "M3"]
    assert [m.material_id for m in course.materials_for_topic(" OOP ")] == ["M1", "M3"]
    assert course.materials_for_topic("numpy") == []


def test_many_materials():
    """1,000 materials are stored in order."""
    course = Course("C101", "AI", "T01")
    for number in range(1000):
        course.add_material(_material(f"M{number}"))
    assert len(course.materials) == 1000
    assert course.materials[-1].material_id == "M999"


def test_course_and_material_round_trip():
    """to_dict and from_dict give back the same values."""
    course = Course("C101", "AI", "T01")
    assert Course.from_dict(course.to_dict()).to_dict() == course.to_dict()
    material = _material()
    assert Material.from_dict(material.to_dict()).to_dict() == material.to_dict()


@pytest.mark.parametrize("row", [None, [], "x", {}, {"course_id": "C1"},
                                 {"course_id": "C1", "title": "", "teacher_id": "T1"}])
def test_course_from_dict_invalid(row):
    """Bad rows raise ValidationError."""
    with pytest.raises(ValidationError):
        Course.from_dict(row)


def test_material_from_dict_missing_column():
    """A missing column is refused."""
    with pytest.raises(ValidationError):
        Material.from_dict({"material_id": "M1", "course_id": "C1"})


def test_repr_text():
    """repr shows the key facts."""
    course = Course("C101", "AI", "T01")
    course.enroll("S01")
    assert "1 students" in repr(course)
    assert "M01" in repr(_material())


# ---------- Quiz ----------

def test_empty_quiz():
    """An empty quiz has max score 0 and grades an empty answer list."""
    quiz = Quiz("Q01", "C101", "Empty")
    assert quiz.max_score == 0
    assert quiz.grade_attempt([]) == (0, {})


def test_single_question_quiz():
    """One question: right and wrong answers."""
    quiz = _quiz(1)
    assert quiz.grade_attempt([1]) == (1, {"oop": (1, 1)})
    assert quiz.grade_attempt([0]) == (0, {"oop": (0, 1)})


def test_grade_by_topic():
    """Scores are counted per topic."""
    quiz = _quiz(4)           # oop, files, oop, files
    score, topics = quiz.grade_attempt([1, 0, 1, 1])
    assert score == 3
    assert topics == {"oop": (2, 2), "files": (1, 2)}


@pytest.mark.parametrize("answers", [[], [1], [1, 1, 1, 1], None, "111", 5])
def test_grade_wrong_number_of_answers(answers):
    """Too few, too many or non-list answers are refused."""
    with pytest.raises(ValidationError):
        _quiz(3).grade_attempt(answers)


@pytest.mark.parametrize("bad", [-1, 4, 99, 1.0, "1", None, True])
def test_grade_invalid_answer(bad):
    """Answers must be whole numbers 0-3 (not bool, float or text)."""
    with pytest.raises(ValidationError):
        _quiz(1).grade_attempt([bad])


def test_duplicate_question_id():
    """The same question ID cannot be added twice."""
    quiz = _quiz(1)
    with pytest.raises(DuplicateError):
        quiz.add_question(make_question("Q0", "Again?", list("abcd"), 0, "oop"))
    assert quiz.max_score == 1


@pytest.mark.parametrize("options", [[], ["a", "b"], list("abcde"), None, "abcd",
                                     ["a", "b", "c", ""]])
def test_make_question_bad_options(options):
    """Exactly 4 non-empty options are needed."""
    with pytest.raises(ValidationError):
        make_question("Q1", "Text?", options, 0, "oop")


@pytest.mark.parametrize("index", [-1, 4, "1", 1.5, None, True])
def test_make_question_bad_answer_index(index):
    """answer_index must be a whole number 0-3."""
    with pytest.raises(ValidationError):
        make_question("Q1", "Text?", list("abcd"), index, "oop")


@pytest.mark.parametrize("bad", ["not a tuple", (1, 2), ["Q", "t", "o", 0, "x"],
                                 None])
def test_add_question_rejects_non_question(bad):
    """Only Question-shaped tuples are accepted."""
    with pytest.raises(ValidationError):
        _quiz(0).add_question(bad)


def test_question_is_immutable_tuple():
    """A Question cannot be changed after it is made."""
    question = make_question("Q1", "Text?", list("abcd"), 2, "OOP")
    assert isinstance(question, Question) and isinstance(question.options, tuple)
    assert question.topic == "oop"
    with pytest.raises(AttributeError):
        question.answer_index = 0


def test_large_quiz_grading():
    """A 10,000-question quiz is graded correctly."""
    quiz = _quiz(10_000, topics=("a", "b", "c", "d", "e"))
    score, topics = quiz.grade_attempt([1] * 5000 + [0] * 5000)
    assert score == 5000
    assert sum(total for _, total in topics.values()) == 10_000


def test_quiz_round_trip():
    """to_dict then from_dict gives an identical quiz."""
    quiz = _quiz(5)
    again = Quiz.from_dict(quiz.to_dict())
    assert again.to_dict() == quiz.to_dict()
    assert again.questions == quiz.questions


@pytest.mark.parametrize("record", [None, [], "x", {}, {"quiz_id": "Q1"},
                                    {"quiz_id": "Q1", "course_id": "C1",
                                     "title": "T", "questions": "no"},
                                    {"quiz_id": "Q1", "course_id": "C1",
                                     "title": "T", "questions": ["bad"]},
                                    {"quiz_id": "Q1", "course_id": "C1",
                                     "title": "T", "questions": [{}]}])
def test_quiz_from_dict_invalid(record):
    """Malformed quiz records raise ValidationError."""
    with pytest.raises(ValidationError):
        Quiz.from_dict(record)


def test_quiz_from_dict_duplicate_questions():
    """Two questions with one ID are refused."""
    record = _quiz(1).to_dict()
    record["questions"] = record["questions"] * 2
    with pytest.raises(DuplicateError):
        Quiz.from_dict(record)


# ---------- weak topics, merging, revision ----------

def test_merge_topic_results_empty_and_single():
    """Merging nothing gives {}; one dict is copied."""
    assert merge_topic_results([]) == {}
    assert merge_topic_results([{"oop": (1, 2)}]) == {"oop": (1, 2)}


def test_merge_topic_results_adds_up():
    """Sums are added per topic and the inputs stay unchanged."""
    first, second = {"oop": (1, 2), "files": (0, 1)}, {"oop": (2, 2)}
    assert merge_topic_results([first, second]) == {"oop": (3, 4), "files": (0, 1)}
    assert first == {"oop": (1, 2), "files": (0, 1)}


def test_weak_topics_empty_and_none_weak():
    """No topics or all strong gives []."""
    assert weak_topics({}) == []
    assert weak_topics({"oop": (3, 3)}) == []


def test_weak_topics_order_and_ties():
    """Weakest first; equal ratios are alphabetical; total 0 is skipped."""
    results = {"zeta": (1, 4), "alpha": (1, 4), "mid": (1, 2), "none": (0, 0),
               "ok": (3, 4)}
    assert weak_topics(results) == ["alpha", "zeta", "mid"]


def test_weak_topics_threshold_edges():
    """Exactly at the threshold is not weak; 0 and 1 are allowed."""
    assert weak_topics({"a": (3, 5)}, 0.6) == []
    assert weak_topics({"a": (0, 5)}, 0) == []
    assert weak_topics({"a": (4, 5)}, 1) == ["a"]


@pytest.mark.parametrize("threshold", [-0.1, 1.1, "0.5", None, True])
def test_weak_topics_bad_threshold(threshold):
    """Thresholds outside 0-1 or not numbers are refused."""
    with pytest.raises(ValidationError):
        weak_topics({"a": (0, 1)}, threshold)


@pytest.mark.parametrize("bad", [None, [], "x", 5])
def test_weak_topics_needs_dict(bad):
    """topic_results must be a dict."""
    with pytest.raises(ValidationError):
        weak_topics(bad)


def test_weak_topics_many_topics():
    """10,000 topics are ranked weakest first."""
    results = {f"t{n:05d}": (n % 5, 5) for n in range(10_000)}
    ranked = weak_topics(results)
    assert len(ranked) == 6000           # ratios 0, .2, .4 are below 0.6
    assert results[ranked[0]][0] == 0


def test_suggest_revision_links_notes():
    """Weak topics get their notes; a topic with no notes gets []."""
    course = Course("C101", "AI", "T01")
    course.add_material(_material("M1", topic="oop"))
    tips = suggest_revision({"oop": (0, 2), "files": (0, 1), "ok": (2, 2)}, course)
    assert [topic for topic, _ in tips] == ["files", "oop"] or \
           [topic for topic, _ in tips] == ["oop", "files"]
    notes = dict(tips)
    assert [m.material_id for m in notes["oop"]] == ["M1"]
    assert notes["files"] == []


def test_suggest_revision_empty():
    """Nothing weak means no suggestions."""
    assert suggest_revision({}, Course("C101", "AI", "T01")) == []
