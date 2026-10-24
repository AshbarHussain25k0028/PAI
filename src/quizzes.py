"""Multiple-choice quizzes, grading by topic and revision suggestions.

Owner: Muhammad Mudassir (Part 4: quizzes, Part 7: revision suggestions)
Lab concepts: Lab 03 (tuple, list, dict), Lab 04 (lambda with sorted).

Key data structures
-------------------
- Question       : a namedtuple (a tuple with field names), so it cannot be
                   changed by accident once the teacher has approved it.
- Quiz.questions : list[Question], kept in the order students see them.
- topic results  : dict {topic: (correct, total)}, built while grading.

INTERFACE STUB (Part 1): bodies are written in Parts 4 and 7.
"""

from __future__ import annotations

from collections import namedtuple

# options is a tuple of 4 strings; answer_index is 0-3.
Question = namedtuple("Question",
                      ["question_id", "text", "options", "answer_index", "topic"])


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
        raise NotImplementedError("Part 4")

    def add_question(self, question: Question) -> None:
        """Append a question to the end of the quiz.

        Args:
            question: a Question with 4 options and answer_index 0-3.
        Raises:
            DuplicateError: if the question ID is already in the quiz.
            ValidationError: if it does not have 4 options or a valid answer.
        Complexity: O(n) for n questions (the duplicate check).
        """
        raise NotImplementedError("Part 4")

    @property
    def max_score(self) -> int:
        """The highest possible score.

        Returns:
            the number of questions (1 mark each).
        Complexity: O(1).
        """
        raise NotImplementedError("Part 4")

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
        raise NotImplementedError("Part 4")

    def to_dict(self) -> dict:
        """Quiz and its questions as nested dicts/lists for JSON.

        Returns:
            dict in the same shape as one record of quizzes.json.
        Complexity: O(n) for n questions.
        """
        raise NotImplementedError("Part 4")

    @classmethod
    def from_dict(cls, record: dict) -> "Quiz":
        """Build a Quiz from one JSON record.

        Args:
            record: dict with quiz_id, course_id, title and a questions list.
        Returns:
            a new Quiz with its questions.
        Raises:
            ValidationError: if a field is missing or a question is invalid.
        Complexity: O(n) for n questions.
        """
        raise NotImplementedError("Part 4")


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
