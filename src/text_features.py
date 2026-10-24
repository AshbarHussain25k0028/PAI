"""Text cleaning and TF-IDF features for question topics (Track A: text).

Owner: Muhammad Mudassir (Part 12)
Lab concepts: Lab 12 (text cleaning, stop-words, Bag-of-Words, TF-IDF).

How it works
------------
clean_text() is our own function: HTML unescape, lowercase, remove
punctuation and digits, drop stop-words. Its output feeds a TF-IDF
vectoriser that is fitted on the TRAINING questions only, so the test
questions stay unseen.

Key data structure: STOP_WORDS is a set, so "is this a stop-word?" is O(1).

INTERFACE STUB (Part 1): bodies are written in Part 12.
"""

from __future__ import annotations

# A small, readable stop-word list; Part 12 may extend it.
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "in", "on", "to",
    "for", "and", "or", "which", "what", "who", "how", "this", "that",
    "with", "by", "as", "at", "it", "its", "from", "be", "does", "did",
}


def clean_text(text: str) -> str:
    """Normalise one piece of text.

    Args:
        text: raw question text (may contain HTML codes like &quot;).
    Returns:
        lowercase words without punctuation, digits or stop-words,
        joined by single spaces.
    Raises:
        ValidationError: if text is not a str.
    Complexity: O(k) for k characters.
    """
    raise NotImplementedError("Part 12")


def tokenize(text: str) -> list[str]:
    """Split cleaned text into words.

    Args:
        text: raw or cleaned text.
    Returns:
        list of words from clean_text(text).
    Complexity: O(k) for k characters.
    """
    raise NotImplementedError("Part 12")


def fit_vectorizer(train_texts: list[str]):
    """Fit a TF-IDF vectoriser on the training texts only.

    Args:
        train_texts: raw training questions.
    Returns:
        (vectorizer, X_train) where X_train is a sparse matrix.
    Raises:
        ValidationError: if train_texts is empty.
    Complexity: O(N) for N words in all training texts.
    """
    raise NotImplementedError("Part 12")


def transform_texts(vectorizer, texts: list[str]):
    """Turn new texts into TF-IDF vectors with an already fitted vectoriser.

    Args:
        vectorizer: from fit_vectorizer().
        texts: raw texts (for example the test questions).
    Returns:
        sparse matrix with one row per text.
    Complexity: O(N) for N words.
    """
    raise NotImplementedError("Part 12")


def search(query: str, texts: list[str], top_k: int = 5) -> list[tuple]:
    """Optional: rank texts by TF-IDF cosine similarity to a query.

    Args:
        query: words typed by the user.
        texts: the questions or notes to search.
        top_k: how many results to return.
    Returns:
        [(index, score), ...], best match first.
    Raises:
        ValidationError: if query is empty or top_k < 1.
    Complexity: O(n * v) for n texts and v vocabulary size.
    """
    raise NotImplementedError("Part 12")
