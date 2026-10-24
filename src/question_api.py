"""Practice questions from the Open Trivia DB API, with an offline cache.

Owner: Muhammad Mudassir (Part 9)
Lab concepts: Lab 06 (requests, status codes, JSON, exceptions).

How it works
------------
1. fetch_questions() calls https://opentdb.com/api.php with a timeout and
   checks both the HTTP status code and the API's own response_code.
2. Good replies are saved to data/raw/opentdb_cache.json.
3. If the internet is down, load_cache() is used instead, so the LMS
   still works offline.

Categories used: Computers 18, Mathematics 19, Science & Nature 17,
History 23. The API allows one call every 5 seconds.

Key data structure: the cache is a dict {category_name: [question dicts]}.

INTERFACE STUB (Part 1): bodies are written in Part 9.
"""

from __future__ import annotations

API_URL = "https://opentdb.com/api.php"
CATEGORIES = {"Computers": 18, "Mathematics": 19,
              "Science & Nature": 17, "History": 23}
TIMEOUT_SECONDS = 10      # always passed to requests.get(timeout=...)
RATE_LIMIT_SECONDS = 5    # wait between two API calls


def fetch_questions(category_id: int, amount: int = 50) -> list[dict]:
    """Download multiple-choice questions for one category.

    Args:
        category_id: one of the values in CATEGORIES.
        amount: how many questions to ask for (1-50).
    Returns:
        list of question dicts as sent by the API.
    Raises:
        APIUnavailableError: no connection, timeout, bad status code,
            bad JSON or response_code other than 0.
        ValidationError: unknown category_id or amount out of range.
    Complexity: O(q) for q questions in the reply.
    """
    raise NotImplementedError("Part 9")


def load_cache(path=None) -> dict:
    """Read the cached questions.

    Args:
        path: cache file; defaults to data/raw/opentdb_cache.json.
    Returns:
        {category_name: [question dicts]}; empty dict if no cache yet.
    Raises:
        DataFileError: if the cache file is malformed.
    Complexity: O(q) for q cached questions.
    """
    raise NotImplementedError("Part 9")


def save_cache(cache: dict, path=None) -> None:
    """Write the cache to disk safely.

    Args:
        cache: {category_name: [question dicts]}.
        path: cache file; defaults to data/raw/opentdb_cache.json.
    Raises:
        DataFileError: if the file cannot be written.
    Complexity: O(q) for q questions.
    """
    raise NotImplementedError("Part 9")


def build_cache(per_category: int = 150) -> dict:
    """Fetch about per_category questions for every category, waiting
    RATE_LIMIT_SECONDS between calls, and merge them without duplicates.

    Args:
        per_category: target number of questions per category.
    Returns:
        the updated cache dict.
    Raises:
        APIUnavailableError: if the API cannot be reached at all.
    Complexity: O(k * q) for k categories and q questions each.
    """
    raise NotImplementedError("Part 9")


def to_quiz_question(api_question: dict, question_id: str, topic: str):
    """Turn one API question into our Question tuple.

    Args:
        api_question: one item from the API reply (HTML-escaped text).
        question_id: new ID for it.
        topic: topic tag to store with it.
    Returns:
        quizzes.Question with 4 shuffled options and the right answer_index.
    Raises:
        ValidationError: if it does not have exactly 3 wrong answers.
    Complexity: O(1).
    """
    raise NotImplementedError("Part 9")
