"""Edge-case tests for scores.py, text_features.py and question_api.py.

Owner: Muhammad Mudassir (Part 16)
Cases: empty input, one element, duplicates, large input, invalid input,
missing file, malformed JSON, API offline (requests.get is monkeypatched, so
no real network call is made).
"""

import json
import warnings

import numpy as np
import pytest
import requests

import question_api
from exceptions import APIUnavailableError, DataFileError, ValidationError
from question_api import (CATEGORIES, fetch_questions, load_cache,
                          merge_questions, practice_set, save_cache,
                          to_quiz_question)
from scores import (loop_vs_vector_demo, missing_mask, quiz_averages,
                    score_matrix, student_averages, to_percentages)
from text_features import (STOP_WORDS, clean_text, fit_vectorizer, search,
                           tokenize, transform_texts)


def _attempt(student, quiz, score, when="2026-11-01 10:00"):
    """Build one attempt record."""
    return {"student_id": student, "quiz_id": quiz, "score": score,
            "attempted_on": when}


# ---------- scores: matrix ----------

def test_score_matrix_empty_everything():
    """No students, quizzes or attempts gives an empty 0x0 matrix."""
    assert score_matrix([], [], []).shape == (0, 0)


def test_score_matrix_no_attempts_is_all_nan():
    """Students and quizzes but no attempts: every cell is NaN."""
    matrix = score_matrix([], ["S1", "S2"], ["Q1"])
    assert matrix.shape == (2, 1) and np.isnan(matrix).all()


def test_score_matrix_single_cell():
    """One student, one quiz, one attempt."""
    assert score_matrix([_attempt("S1", "Q1", 4)], ["S1"], ["Q1"])[0, 0] == 4


def test_score_matrix_latest_attempt_wins():
    """A retake replaces the earlier attempt, whatever the list order."""
    attempts = [_attempt("S1", "Q1", 9, "2026-11-05 10:00"),
                _attempt("S1", "Q1", 2, "2026-11-01 10:00")]
    assert score_matrix(attempts, ["S1"], ["Q1"])[0, 0] == 9


def test_score_matrix_places_scores_and_leaves_gaps():
    """Scores land in the right row/column; missing ones stay NaN."""
    attempts = [_attempt("S2", "Q2", 7), _attempt("S1", "Q1", 3)]
    matrix = score_matrix(attempts, ["S1", "S2"], ["Q1", "Q2"])
    assert matrix[0, 0] == 3 and matrix[1, 1] == 7
    assert np.isnan(matrix[0, 1]) and np.isnan(matrix[1, 0])


@pytest.mark.parametrize("students, quizzes", [(["S1", "S1"], ["Q1"]),
                                               (["S1"], ["Q1", "Q1"])])
def test_score_matrix_duplicate_ids(students, quizzes):
    """Duplicate student or quiz IDs are refused."""
    with pytest.raises(ValidationError):
        score_matrix([], students, quizzes)


@pytest.mark.parametrize("attempt", [_attempt("S9", "Q1", 1), _attempt("S1", "Q9", 1),
                                     {"student_id": "S1", "quiz_id": "Q1"},
                                     _attempt("S1", "Q1", "high"),
                                     _attempt("S1", "Q1", None), "nope", None])
def test_score_matrix_invalid_attempt(attempt):
    """Unknown IDs, missing fields and non-numeric scores are refused."""
    with pytest.raises(ValidationError):
        score_matrix([attempt], ["S1"], ["Q1"])


def test_score_matrix_large():
    """10,000 students x 50 quizzes, every cell filled."""
    students = [f"S{n}" for n in range(10_000)]
    quizzes = [f"Q{n}" for n in range(50)]
    attempts = [_attempt(s, q, 1.0) for s in students[:2000] for q in quizzes]
    matrix = score_matrix(attempts, students, quizzes)
    assert matrix.shape == (10_000, 50)
    assert int((~np.isnan(matrix)).sum()) == 2000 * 50


# ---------- scores: percentages, masks, averages ----------

def test_to_percentages_broadcasts_and_keeps_nan():
    """Each column is divided by its own max; NaN stays NaN."""
    result = to_percentages([[5, np.nan], [10, 2]], [10, 4])
    assert result[0, 0] == 50 and result[1, 0] == 100 and result[1, 1] == 50
    assert np.isnan(result[0, 1])


def test_to_percentages_empty_matrix():
    """An empty (0, 0) matrix with no maxima is fine."""
    assert to_percentages(np.empty((0, 0)), []).shape == (0, 0)


@pytest.mark.parametrize("maxima", [[10], [10, 0], [10, -1], [10, np.nan],
                                    [10, "x"], [[10, 10]]])
def test_to_percentages_bad_max_scores(maxima):
    """Wrong shape, zero, negative, NaN or text maxima are refused."""
    with pytest.raises(ValidationError):
        to_percentages([[1, 2]], maxima)


@pytest.mark.parametrize("matrix", [[1, 2, 3], [[[1]]], [["a", "b"]], 5, [[1], [2, 3]]])
def test_matrix_functions_reject_bad_input(matrix):
    """Non-2-D or non-numeric input is refused by every matrix function."""
    for function in (missing_mask, quiz_averages, student_averages):
        with pytest.raises(ValidationError):
            function(matrix)


def test_missing_mask():
    """True exactly where the value is NaN."""
    mask = missing_mask([[1, np.nan], [np.nan, np.nan]])
    assert mask.tolist() == [[False, True], [True, True]]


def test_averages_ignore_missing_without_warning():
    """A NaN row/column gives NaN and no RuntimeWarning."""
    matrix = [[10, np.nan], [20, np.nan], [np.nan, np.nan]]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        quizzes = quiz_averages(matrix)
        students = student_averages(matrix)
    assert quizzes[0] == 15 and np.isnan(quizzes[1])
    assert students[0] == 10 and students[1] == 20 and np.isnan(students[2])


def test_averages_single_element_and_empty():
    """One cell is its own mean; an empty matrix gives empty arrays."""
    assert quiz_averages([[7]]).tolist() == [7]
    assert student_averages(np.empty((0, 3))).shape == (0,)
    assert quiz_averages(np.empty((0, 3))).shape == (3,)


def test_averages_match_nanmean_on_large_matrix():
    """1000x50 matrix with 20% missing agrees with np.nanmean."""
    rng = np.random.default_rng(0)
    matrix = rng.integers(0, 101, (1000, 50)).astype(float)
    matrix[rng.random((1000, 50)) < 0.2] = np.nan
    assert np.allclose(quiz_averages(matrix), np.nanmean(matrix, axis=0))
    assert np.allclose(student_averages(matrix), np.nanmean(matrix, axis=1))


def test_loop_vs_vector_demo():
    """The demo returns two timings and refuses bad sizes."""
    loop_s, vector_s = loop_vs_vector_demo(1000)
    assert loop_s >= 0 and vector_s >= 0
    for bad in (0, -5, 1.5, "10", True, None):
        with pytest.raises(ValidationError):
            loop_vs_vector_demo(bad)


# ---------- text_features ----------

def test_clean_text_basics():
    """Lowercase, unescape, drop punctuation, digits and stop-words."""
    assert clean_text("") == ""
    assert clean_text("   ") == ""
    assert clean_text("The CPU &amp; RAM: 2 chips!") == "cpu ram chips"
    assert clean_text("&quot;Hello&quot;") == "hello"


def test_clean_text_only_stop_words_or_symbols():
    """Text with no usable words becomes an empty string."""
    assert clean_text("the of and") == ""
    assert clean_text("123 !!! ???") == ""


def test_clean_text_is_stable_and_handles_unicode():
    """Cleaning twice changes nothing; accented letters are treated as separators."""
    once = clean_text("Mixed CASE, words... 42")
    assert clean_text(once) == once
    assert "caf" in clean_text("Café")


@pytest.mark.parametrize("bad", [None, 5, ["a"], b"bytes"])
def test_clean_text_rejects_non_text(bad):
    """Only strings are accepted."""
    with pytest.raises(ValidationError):
        clean_text(bad)


def test_clean_text_large_input():
    """A very long text (1 million characters) still works."""
    text = "python data " * 90_000
    assert len(text) > 1_000_000
    assert tokenize(text)[:2] == ["python", "data"]


def test_stop_words_is_a_set():
    """Stop-words are kept in a set for O(1) lookup."""
    assert isinstance(STOP_WORDS, set)


def test_fit_vectorizer_empty_and_unusable():
    """No texts, or texts without words, are refused."""
    with pytest.raises(ValidationError):
        fit_vectorizer([])
    with pytest.raises(ValidationError):
        fit_vectorizer(["the of and", "123"])


def test_fit_vectorizer_single_text_and_duplicates():
    """One text works; identical texts give identical rows."""
    _, matrix = fit_vectorizer(["python lists"])
    assert matrix.shape[0] == 1
    _, matrix = fit_vectorizer(["python lists", "python lists"])
    assert (matrix[0] != matrix[1]).nnz == 0


def test_transform_uses_training_vocabulary_only():
    """Unseen words in new texts are ignored, not added."""
    vectorizer, _ = fit_vectorizer(["python lists", "numpy arrays"])
    size = len(vectorizer.vocabulary_)
    result = transform_texts(vectorizer, ["python dragons"])
    assert result.shape == (1, size)
    assert len(vectorizer.vocabulary_) == size
    assert transform_texts(vectorizer, []).shape == (0, size)


def test_search_empty_and_no_match():
    """No texts gives []; a query that matches nothing gives []."""
    assert search("python", []) == []
    assert search("zebra", ["python lists", "numpy arrays"]) == []


def test_search_ranks_best_first_and_limits():
    """The best match is first and top_k limits the count."""
    texts = ["history of rome", "python lists and dicts", "python python numpy"]
    found = search("python", texts, top_k=1)
    assert len(found) == 1 and found[0][0] in (1, 2)
    both = search("python", texts, top_k=10)
    assert [i for i, _ in both] != [0]
    assert all(score > 0 for _, score in both)
    assert both[0][1] >= both[-1][1]


def test_search_single_text():
    """One text can be found."""
    assert search("python", ["python lists"])[0][0] == 0


@pytest.mark.parametrize("query", ["", "   ", None, 5])
def test_search_invalid_query(query):
    """Empty or non-text queries are refused."""
    with pytest.raises(ValidationError):
        search(query, ["python"])


@pytest.mark.parametrize("top_k", [0, -1, 1.5, "3", None])
def test_search_invalid_top_k(top_k):
    """top_k must be a whole number of at least 1."""
    with pytest.raises(ValidationError):
        search("python", ["python"], top_k=top_k)


def test_search_large_corpus():
    """10,000 texts are searched and the one special text is found."""
    texts = [f"common words item{n % 50}" for n in range(10_000)]
    texts[1234] = "unique zebra stripes"
    assert search("zebra", texts, top_k=1)[0][0] == 1234


# ---------- question_api: offline and bad replies ----------

class FakeReply:
    """A stand-in for requests.Response."""

    def __init__(self, status=200, payload=None, bad_json=False):
        self.status_code = status
        self._payload = payload
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("not json")
        return self._payload


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Skip the 5-second rate-limit sleep so tests stay fast."""
    monkeypatch.setattr(question_api, "_wait_for_rate_limit", lambda: None)


def _patch_get(monkeypatch, reply=None, error=None):
    """Replace requests.get so no real network call is made."""
    def fake_get(*args, **kwargs):
        assert "timeout" in kwargs          # the rule: always pass a timeout
        if error is not None:
            raise error
        return reply
    monkeypatch.setattr(question_api.requests, "get", fake_get)


@pytest.mark.parametrize("error", [requests.ConnectionError("down"),
                                   requests.Timeout("slow"),
                                   requests.RequestException("other")])
def test_fetch_offline_raises_api_error(monkeypatch, error):
    """Network failures become APIUnavailableError."""
    _patch_get(monkeypatch, error=error)
    with pytest.raises(APIUnavailableError):
        fetch_questions(18, 5)


@pytest.mark.parametrize("status", [404, 429, 500, 503])
def test_fetch_bad_status(monkeypatch, status):
    """Any HTTP status other than 200 is an error."""
    _patch_get(monkeypatch, FakeReply(status))
    with pytest.raises(APIUnavailableError):
        fetch_questions(18, 5)


@pytest.mark.parametrize("reply", [FakeReply(bad_json=True), FakeReply(payload=[1]),
                                   FakeReply(payload="text"), FakeReply(payload=None)])
def test_fetch_bad_json_shape(monkeypatch, reply):
    """Replies that are not a JSON object are refused."""
    _patch_get(monkeypatch, reply)
    with pytest.raises(APIUnavailableError):
        fetch_questions(18, 5)


@pytest.mark.parametrize("code", [2, 3, 4, 5, None])
def test_fetch_bad_response_code(monkeypatch, code):
    """A response_code other than 0 or 1 is an error."""
    _patch_get(monkeypatch, FakeReply(payload={"response_code": code, "results": []}))
    with pytest.raises(APIUnavailableError):
        fetch_questions(18, 5)


def test_fetch_code_zero_without_results_list(monkeypatch):
    """response_code 0 but no results list is an error."""
    _patch_get(monkeypatch, FakeReply(payload={"response_code": 0}))
    with pytest.raises(APIUnavailableError):
        fetch_questions(18, 5)


def test_fetch_not_enough_questions_gives_empty_list(monkeypatch):
    """response_code 1 means 'category too small', not a failure."""
    _patch_get(monkeypatch, FakeReply(payload={"response_code": 1, "results": []}))
    assert fetch_questions(19, 50) == []


def test_fetch_success(monkeypatch):
    """A good reply returns the results list."""
    results = [{"question": "Q?"}]
    _patch_get(monkeypatch, FakeReply(payload={"response_code": 0, "results": results}))
    assert fetch_questions(18, 1) == results


@pytest.mark.parametrize("category, amount", [(999, 5), ("18", 5), (None, 5),
                                              (18, 0), (18, 51), (18, -1),
                                              (18, 2.5), (18, "5"), (18, True)])
def test_fetch_validates_arguments_before_calling(monkeypatch, category, amount):
    """Bad arguments never reach the network."""
    def boom(*args, **kwargs):
        raise AssertionError("network must not be called")
    monkeypatch.setattr(question_api.requests, "get", boom)
    with pytest.raises(ValidationError):
        fetch_questions(category, amount)


# ---------- question_api: cache ----------

def test_load_cache_missing_file(tmp_path):
    """No cache file yet is not an error."""
    assert load_cache(tmp_path / "none.json") == {}


def test_load_cache_malformed_json(tmp_path):
    """Broken JSON raises DataFileError."""
    path = tmp_path / "cache.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(DataFileError):
        load_cache(path)


@pytest.mark.parametrize("content", ["[]", '"text"', "5", '{"History": "oops"}',
                                     '{"History": {"a": 1}}', "null"])
def test_load_cache_wrong_shape(tmp_path, content):
    """The cache must map each category to a list."""
    path = tmp_path / "cache.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(DataFileError):
        load_cache(path)


def test_cache_empty_object_and_round_trip(tmp_path):
    """An empty cache loads as {}; saved data comes back unchanged."""
    path = tmp_path / "cache.json"
    path.write_text("{}", encoding="utf-8")
    assert load_cache(path) == {}
    cache = {"History": [{"question": "Who &amp; why?"}]}
    save_cache(cache, path)
    assert load_cache(path) == cache


def test_save_cache_unwritable_folder(tmp_path):
    """Saving to a place that is not a folder raises DataFileError."""
    blocker = tmp_path / "a_file"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(DataFileError):
        save_cache({}, blocker / "cache.json")


def test_merge_questions_empty_and_duplicates():
    """Empty lists add nothing; repeated texts are added only once."""
    assert merge_questions([], []) == 0
    old = [{"question": "A"}]
    assert merge_questions(old, []) == 0
    assert merge_questions(old, [{"question": "A"}, {"question": "B"},
                                 {"question": "B"}]) == 1
    assert [q["question"] for q in old] == ["A", "B"]


def test_merge_questions_large():
    """20,000 new questions with half already present."""
    old = [{"question": str(n)} for n in range(10_000)]
    new = [{"question": str(n)} for n in range(5_000, 15_000)]
    assert merge_questions(old, new) == 5_000
    assert len(old) == 15_000


# ---------- question_api: converting and practice sets ----------

def _api_question(text="What is 2 &amp; 2?"):
    """One question in the API's format."""
    return {"question": text, "correct_answer": "4 &amp; more",
            "incorrect_answers": ["1", "2", "3"]}


def test_to_quiz_question_unescapes_and_keeps_answer():
    """HTML codes are decoded and answer_index points at the right option."""
    question = to_quiz_question(_api_question(), "P1", "Computers")
    assert question.text == "What is 2 & 2?"
    assert question.options[question.answer_index] == "4 & more"
    assert len(question.options) == 4 and question.topic == "computers"


@pytest.mark.parametrize("change", [{"incorrect_answers": ["a", "b"]},
                                    {"incorrect_answers": None},
                                    {"incorrect_answers": "abc"},
                                    {"correct_answer": None},
                                    {"correct_answer": 5}])
def test_to_quiz_question_malformed(change):
    """Wrong answer lists or a missing right answer are refused."""
    item = dict(_api_question(), **change)
    with pytest.raises(ValidationError):
        to_quiz_question(item, "P1", "history")


def test_to_quiz_question_empty_text():
    """An empty question text is refused."""
    with pytest.raises(ValidationError):
        to_quiz_question(_api_question(""), "P1", "history")


def test_practice_set_offline_uses_cache(monkeypatch, tmp_path):
    """With the API down, questions come from the cache."""
    _patch_get(monkeypatch, error=requests.ConnectionError("down"))
    path = tmp_path / "cache.json"
    save_cache({"History": [_api_question(f"Q{n}?") for n in range(10)]}, path)
    questions, source = practice_set("History", 3, path)
    assert source == "offline cache" and len(questions) == 3
    assert len({q.question_id for q in questions}) == 3


def test_practice_set_cache_smaller_than_count(monkeypatch, tmp_path):
    """Asking for more than the cache holds returns what exists."""
    _patch_get(monkeypatch, error=requests.Timeout("slow"))
    path = tmp_path / "cache.json"
    save_cache({"History": [_api_question("Only one?")]}, path)
    questions, _ = practice_set("History", 5, path)
    assert len(questions) == 1


def test_practice_set_offline_no_cache(monkeypatch, tmp_path):
    """Offline with no cache file (or an empty category) gives a clear error."""
    _patch_get(monkeypatch, error=requests.ConnectionError("down"))
    with pytest.raises(APIUnavailableError):
        practice_set("History", 3, tmp_path / "missing.json")
    path = tmp_path / "cache.json"
    save_cache({"History": []}, path)
    with pytest.raises(APIUnavailableError):
        practice_set("History", 3, path)


def test_practice_set_offline_malformed_cache(monkeypatch, tmp_path):
    """Offline with a broken cache file raises DataFileError."""
    _patch_get(monkeypatch, error=requests.ConnectionError("down"))
    path = tmp_path / "cache.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(DataFileError):
        practice_set("History", 3, path)


def test_practice_set_online(monkeypatch, tmp_path):
    """A good live reply is used and reported as online."""
    reply = FakeReply(payload={"response_code": 0, "results": [_api_question()]})
    _patch_get(monkeypatch, reply)
    questions, source = practice_set("Computers", 1, tmp_path / "unused.json")
    assert source == "online" and len(questions) == 1


@pytest.mark.parametrize("name", ["", "history", None, "Art"])
def test_practice_set_unknown_category(name):
    """Category names must be keys of CATEGORIES."""
    with pytest.raises(ValidationError):
        practice_set(name)


def test_committed_cache_is_valid():
    """The cache committed in the repo loads and covers all categories."""
    cache = load_cache()
    assert set(CATEGORIES) <= set(cache)
    assert all(len(cache[name]) > 0 for name in CATEGORIES)
