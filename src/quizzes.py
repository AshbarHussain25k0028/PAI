"""Multiple-choice quizzes, grading by topic and revision suggestions.

Owner: Muhammad Mudassir (Part 4: quizzes, Part 7: revision suggestions)
Lab concepts: Lab 03 (tuple, list, dict), Lab 04 (lambda with sorted).

Key data structures
-------------------
- Question       : a namedtuple (a tuple with field names), so it cannot be
                   changed by accident once the teacher has approved it.
- Quiz.questions : list[Question], kept in the order students see them.
- topic results  : dict {topic: (correct, total)}, built while grading.

weak_topics() and suggest_revision() are still stubs: they are written in Part 7.
"""

from __future__ import annotations

from collections import namedtuple

from exceptions import DuplicateError, ValidationError
from utils import require_text

# options is a tuple of 4 strings; answer_index is 0-3.
Question = namedtuple("Question",
                      ["question_id", "text", "options", "answer_index", "topic"])

# Every question has exactly this many options (A, B, C, D).
OPTION_COUNT = 4


def _check_index(value, field: str) -> int:
    """Check that a value is a whole number from 0 to 3.

    Args:
        value: the value to check (an answer or an answer_index).
        field: the field name, used in the error message.
    Returns:
        the value as an int.
    Raises:
        ValidationError: if it is not an int, is a bool, or is outside 0-3.
    Complexity: O(1).
    """
    # bool is a subclass of int in Python, so True would sneak through as 1.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"'{field}' must be a whole number 0-3.")
    if not 0 <= value < OPTION_COUNT:
        raise ValidationError(f"'{field}' must be between 0 and 3, got {value}.")
    return value


def make_question(question_id, text, options, answer_index, topic) -> Question:
    """Check every field and build a Question tuple.

    Helper added in Part 4, used by add_question() and from_dict().

    Args:
        question_id: e.g. "Q01-1".
        text: the question shown to the student.
        options: 4 option strings (list or tuple).
        answer_index: index of the right option, 0-3.
        topic: topic tag such as "oop" (stored in lower case).
    Returns:
        a new Question with options stored as a tuple.
    Raises:
        ValidationError: if a field is empty or there are not 4 options.
    Complexity: O(1) (always 4 options).
    """
    if not isinstance(options, (list, tuple)) or len(options) != OPTION_COUNT:
        raise ValidationError(
            f"Question {question_id} must have exactly {OPTION_COUNT} options.")
    clean_options = tuple(require_text(option, "option") for option in options)
    return Question(require_text(question_id, "question_id"),
                    require_text(text, "text"),
                    clean_options,
                    _check_index(answer_index, "answer_index"),
                    require_text(topic, "topic").lower())


class Quiz:
    """A quiz that belongs to one course.

    Attributes:
        quiz_id (str), course_id (str), title (str), questions (list[Question])
    """

    def __init__(self, quiz_id: str, course_id: str, title: str):
        """Create an empty quiz.

        Args:
            quiz_id: e.g. "Q01".
            course_id: the course it belongs to.
            title: name shown to students.
        Raises:
            ValidationError: if any value is empty.
        Complexity: O(1).
        """
        self.quiz_id = require_text(quiz_id, "quiz_id")
        self.course_id = require_text(course_id, "course_id")
        self.title = require_text(title, "title")
        self.questions: list[Question] = []   # in the order students see them

    def __repr__(self) -> str:
        """Short text form, handy when printing in the console.

        Returns:
            e.g. "Quiz(Q01, 'Data structures and functions', 5 questions)".
        Complexity: O(1).
        """
        return (f"Quiz({self.quiz_id}, {self.title!r}, "
                f"{len(self.questions)} questions)")

    def add_question(self, question: Question) -> None:
        """Append a question to the end of the quiz.

        Args:
            question: a Question with 4 options and answer_index 0-3.
        Raises:
            DuplicateError: if the question ID is already in the quiz.
            ValidationError: if it does not have 4 options or a valid answer.
        Complexity: O(n) for n questions (the duplicate check).
        """
        if not isinstance(question, tuple) or len(question) != len(Question._fields):
            raise ValidationError("Only Question tuples can be added.")
        question = make_question(*question)   # re-check every field
        if any(old.question_id == question.question_id
               for old in self.questions):
            raise DuplicateError(
                f"Question {question.question_id} is already in {self.quiz_id}.")
        self.questions.append(question)

    @property
    def max_score(self) -> int:
        """The highest possible score.

        Returns:
            the number of questions (1 mark each).
        Complexity: O(1).
        """
        return len(self.questions)

    def grade_attempt(self, answers: list[int]) -> tuple[int, dict]:
        """Mark a student's answers.

        Args:
            answers: chosen option index (0-3) for every question, in order.
        Returns:
            (score, topic_results) where topic_results is
            {topic: (correct, total)}.
        Raises:
            ValidationError: wrong number of answers (incomplete attempt) or
            an answer outside 0-3.
        Complexity: O(n) for n questions.
        """
        if not isinstance(answers, (list, tuple)) or len(answers) != self.max_score:
            raise ValidationError(
                f"Expected {self.max_score} answers for {self.quiz_id}.")
        score = 0
        topic_results: dict[str, tuple[int, int]] = {}   # topic -> (correct, total)
        for question, answer in zip(self.questions, answers):
            is_right = _check_index(answer, "answer") == question.answer_index
            correct, total = topic_results.get(question.topic, (0, 0))
            topic_results[question.topic] = (correct + is_right, total + 1)
            score += is_right
        return score, topic_results

    def to_dict(self) -> dict:
        """Quiz and its questions as nested dicts/lists for JSON.

        Returns:
            dict in the same shape as one record of quizzes.json.
        Complexity: O(n) for n questions.
        """
        questions = [dict(question._asdict(), options=list(question.options))
                     for question in self.questions]
        return {"quiz_id": self.quiz_id, "course_id": self.course_id,
                "title": self.title, "questions": questions}

    @classmethod
    def from_dict(cls, record: dict) -> "Quiz":
        """Build a Quiz from one JSON record.

        Args:
            record: dict with quiz_id, course_id, title and a questions list.
        Returns:
            a new Quiz with its questions.
        Raises:
            ValidationError: if a field is missing or a question is invalid.
            DuplicateError: if two questions share an ID.
        Complexity: O(n^2) worst case for n questions (duplicate check on
        each add); n is small (about 5-10 per quiz).
        """
        if not isinstance(record, dict):
            raise ValidationError("Each quiz record must be a dict.")
        quiz = cls(record.get("quiz_id"), record.get("course_id"),
                   record.get("title"))
        questions = record.get("questions")
        if not isinstance(questions, list):
            raise ValidationError(f"Quiz {quiz.quiz_id} needs a questions list.")
        for item in questions:
            if not isinstance(item, dict):
                raise ValidationError(f"Bad question in quiz {quiz.quiz_id}.")
            quiz.add_question(make_question(
                *(item.get(field) for field in Question._fields)))
        return quiz


def weak_topics(topic_results: dict, threshold: float = 0.6) -> list[str]:
    """Topics where correct/total is below threshold, weakest first.

    Uses sorted(..., key=lambda item: ratio) (Lab 04 requirement).

    Args:
        topic_results: {topic: (correct, total)} from Quiz.grade_attempt.
        threshold: ratio below which a topic counts as weak (0-1).
    Returns:
        list of topic names, lowest ratio first.
    Raises:
        ValidationError: if threshold is not between 0 and 1.
    Complexity: O(t log t) for t topics.
    """
    raise NotImplementedError("Part 7")


def suggest_revision(topic_results: dict, course, threshold: float = 0.6) -> list[tuple]:
    """Rule-based revision tips: for each weak topic, the course notes on it.

    Args:
        topic_results: from Quiz.grade_attempt.
        course: the Course the quiz belongs to.
        threshold: passed on to weak_topics().
    Returns:
        [(topic, [Material, ...]), ...], weakest topic first.
    Raises:
        ValidationError: if threshold is not between 0 and 1.
    Complexity: O(t log t + t*m) for t topics and m materials.
    """
    raise NotImplementedError("Part 7")
