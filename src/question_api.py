"""Practice questions from the Open Trivia DB API, with an offline cache.

Owner: Muhammad Mudassir (Part 9)
Lab concepts: Lab 06 (requests, status codes, JSON, exceptions).

How it works
------------
1. fetch_questions() calls https://opentdb.com/api.php with a timeout and
   checks both the HTTP status code and the API's own response_code.
2. Good replies are saved to data/raw/opentdb_cache.json (committed to the
   repo, so a fresh clone works offline and Part 14 has training data).
3. If the internet is down, the saved questions are used instead, so the
   LMS still works offline (see practice_set()).

Categories used: Computers 18, Mathematics 19, Science & Nature 17,
History 23. The API allows one call every 5 seconds, so every call first
waits until 5 seconds have passed since the previous one.

Key data structures
-------------------
- the cache is a dict {category_name: [question dicts]} (the API's own
  format, HTML-escaped text kept as sent).
- a set of question texts per category, so merging never adds a duplicate.

Refresh the cache from the repo root with:  python src/question_api.py
"""

from __future__ import annotations

import html
import random
import time
from pathlib import Path

import requests

from exceptions import APIUnavailableError, DataFileError, LMSError, ValidationError
from quizzes import OPTION_COUNT, make_question
from storage import RAW_DIR, load_json, save_json

API_URL = "https://opentdb.com/api.php"
CATEGORIES = {"Computers": 18, "Mathematics": 19,
              "Science & Nature": 17, "History": 23}
TIMEOUT_SECONDS = 10      # always passed to requests.get(timeout=...)
RATE_LIMIT_SECONDS = 5    # wait between two API calls
CACHE_FILE = RAW_DIR / "opentdb_cache.json"
MAX_AMOUNT = 50           # the API sends at most 50 questions per call
BATCH_SIZE = 25           # per call in build_cache: the server hangs instead
                          # of answering when a small category (Mathematics)
                          # cannot fill 50
MAX_CALLS = 15            # most calls per category in build_cache
MAX_STALE_CALLS = 3       # stop a category after 3 calls with nothing new

# response_code values from the API (https://opentdb.com/api_config.php)
NOT_ENOUGH_QUESTIONS = 1     # the category has fewer than `amount` questions
RESPONSE_MESSAGES = {2: "invalid parameter", 5: "too many requests (rate limit)"}

_last_call = 0.0          # time.monotonic() of the previous API call


def _wait_for_rate_limit() -> None:
    """Sleep until RATE_LIMIT_SECONDS have passed since the last reply.

    Counting from the end of the previous call (not its start) means a slow
    reply can never make two calls arrive closer than the limit.

    Complexity: O(1).
    """
    wait = RATE_LIMIT_SECONDS - (time.monotonic() - _last_call)
    if _last_call and wait > 0:
        time.sleep(wait)


def _get_json(url: str, params: dict) -> dict:
    """GET a URL (after the rate-limit wait) and return the JSON reply.

    Args:
        url: the API address.
        params: query parameters.
    Returns:
        the parsed JSON dict.
    Raises:
        APIUnavailableError: no connection, timeout, HTTP status other
            than 200, or a reply that is not a JSON object.
    Complexity: O(r) for r characters in the reply.
    """
    global _last_call
    _wait_for_rate_limit()
    try:
        reply = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as error:
        raise APIUnavailableError(
            f"Could not reach Open Trivia DB ({type(error).__name__}).") from error
    finally:
        _last_call = time.monotonic()     # the next call waits from here
    if reply.status_code != 200:
        raise APIUnavailableError(
            f"Open Trivia DB answered with HTTP {reply.status_code}.")
    try:
        data = reply.json()
    except ValueError as error:
        raise APIUnavailableError("Open Trivia DB sent a reply that is not JSON.") from error
    if not isinstance(data, dict):
        raise APIUnavailableError("Open Trivia DB sent an unexpected reply.")
    return data


def fetch_questions(category_id: int, amount: int = 50) -> list[dict]:
    """Download multiple-choice questions for one category.

    Args:
        category_id: one of the values in CATEGORIES.
        amount: how many questions to ask for (1-50).
    Returns:
        list of question dicts as sent by the API; empty when the category
        has fewer than `amount` questions (response_code 1).
    Raises:
        APIUnavailableError: no connection, timeout, bad status code,
            bad JSON or another response_code other than 0.
        ValidationError: unknown category_id or amount out of range.
    Complexity: O(q) for q questions in the reply.
    """
    if category_id not in CATEGORIES.values():
        raise ValidationError(f"Unknown category {category_id}.")
    if isinstance(amount, bool) or not isinstance(amount, int) \
            or not 1 <= amount <= MAX_AMOUNT:
        raise ValidationError(f"amount must be a whole number 1-{MAX_AMOUNT}.")
    params = {"amount": amount, "category": category_id, "type": "multiple"}
    data = _get_json(API_URL, params)
    code = data.get("response_code")
    if code == NOT_ENOUGH_QUESTIONS:
        return []
    if code != 0 or not isinstance(data.get("results"), list):
        reason = RESPONSE_MESSAGES.get(code, f"response_code {code}")
        raise APIUnavailableError(f"Open Trivia DB refused the request: {reason}.")
    return data["results"]


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
    path = Path(CACHE_FILE if path is None else path)
    if not path.exists():
        return {}                     # no cache yet is not an error
    cache = load_json(path)
    if not isinstance(cache, dict) or not all(
            isinstance(questions, list) for questions in cache.values()):
        raise DataFileError("The question cache must map each category to a list.")
    return cache


def save_cache(cache: dict, path=None) -> None:
    """Write the cache to disk safely.

    Args:
        cache: {category_name: [question dicts]}.
        path: cache file; defaults to data/raw/opentdb_cache.json.
    Raises:
        DataFileError: if the file cannot be written.
    Complexity: O(q) for q questions.
    """
    save_json(CACHE_FILE if path is None else path, cache)


def merge_questions(old: list[dict], new: list[dict]) -> int:
    """Append the new questions whose text is not already in old.

    Helper added in Part 9, used by build_cache().

    Args:
        old: cached questions of one category (changed in place).
        new: questions just downloaded.
    Returns:
        how many questions were added.
    Complexity: O(o + n), because the seen texts are kept in a set.
    """
    seen = {question.get("question") for question in old}
    added = 0
    for question in new:
        if question.get("question") not in seen:
            seen.add(question.get("question"))
            old.append(question)
            added += 1
    return added


def _fill_category(questions: list[dict], category_id: int,
                   per_category: int) -> None:
    """Keep calling the API until a category has per_category questions.

    Each call returns a random set, so repeats are dropped by
    merge_questions(). The loop stops at the target, after MAX_CALLS calls,
    or after MAX_STALE_CALLS calls in a row that add nothing (the category
    has no more questions). If the category is smaller than the amount
    asked for, the amount is halved.

    Args:
        questions: cached list for this category (changed in place).
        category_id: the Open Trivia DB category.
        per_category: target size of the list.
    Raises:
        APIUnavailableError: if a call fails.
    Complexity: O(c * q) for c calls of q questions.
    """
    amount, stale = BATCH_SIZE, 0
    for _ in range(MAX_CALLS):
        if len(questions) >= per_category or amount < 1 or stale >= MAX_STALE_CALLS:
            return
        batch = fetch_questions(category_id, amount)
        if not batch:
            amount //= 2              # category is smaller: ask for fewer
        elif merge_questions(questions, batch) == 0:
            stale += 1
        else:
            stale = 0


def build_cache(per_category: int = 150) -> dict:
    """Fetch about per_category questions for every category, waiting
    RATE_LIMIT_SECONDS between calls, and merge them without duplicates.

    The cache is saved even when a call fails, so running it again
    continues from what was already downloaded.

    Args:
        per_category: target number of questions per category.
    Returns:
        the updated cache dict.
    Raises:
        APIUnavailableError: if the API cannot be reached at all.
    Complexity: O(k * q) for k categories and q questions each.
    """
    cache = load_cache()
    try:
        for name, category_id in CATEGORIES.items():
            questions = cache.setdefault(name, [])
            _fill_category(questions, category_id, per_category)
            print(f"{name}: {len(questions)} questions cached.")
    finally:
        save_cache(cache)             # keep what we have, even after a failure
    return cache


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
    wrong = api_question.get("incorrect_answers")
    right = api_question.get("correct_answer")
    if not isinstance(wrong, list) or len(wrong) != OPTION_COUNT - 1 \
            or not isinstance(right, str):
        raise ValidationError(
            f"Question {question_id} needs 1 right and {OPTION_COUNT - 1} wrong answers.")
    options = [html.unescape(str(text)) for text in wrong + [right]]
    random.shuffle(options)
    answer_index = options.index(html.unescape(right))
    text = html.unescape(str(api_question.get("question", "")))
    return make_question(question_id, text, options, answer_index, topic)


def practice_set(category_name: str, count: int = 5, cache_path=None):
    """Get practice questions: live from the API, or from the cache offline.

    Args:
        category_name: a key of CATEGORIES.
        count: how many questions (1-50).
        cache_path: cache file; defaults to data/raw/opentdb_cache.json.
    Returns:
        (list of Question tuples, "online" or "offline cache").
    Raises:
        ValidationError: unknown category.
        APIUnavailableError: offline and nothing cached for this category.
        DataFileError: if the cache file is malformed.
    Complexity: O(q) for q cached questions.
    """
    if category_name not in CATEGORIES:
        raise ValidationError(f"Unknown category {category_name!r}.")
    try:
        raw, source = fetch_questions(CATEGORIES[category_name], count), "online"
    except APIUnavailableError:
        raw, source = [], "offline cache"
    if not raw:
        cached = load_cache(cache_path).get(category_name, [])
        if not cached:
            raise APIUnavailableError("No internet and no saved questions yet.")
        raw, source = random.sample(cached, min(count, len(cached))), "offline cache"
    topic = category_name.lower()
    return [to_quiz_question(item, f"P{number}", topic)
            for number, item in enumerate(raw, start=1)], source


if __name__ == "__main__":
    try:
        build_cache()
    except LMSError as error:      # saved categories stay; run again to resume
        print(f"Stopped: {error}")
