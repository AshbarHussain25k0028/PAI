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
"""

from __future__ import annotations

import html
import re

from exceptions import ValidationError

# A small, readable stop-word list (a set: membership test is O(1)).
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "of", "in", "on", "to",
    "for", "and", "or", "which", "what", "who", "how", "this", "that",
    "with", "by", "as", "at", "it", "its", "from", "be", "does", "did",
}

# Anything that is not a lowercase letter or space becomes a space.
_NON_LETTERS = re.compile(r"[^a-z\s]")


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
    if not isinstance(text, str):
        raise ValidationError("Text must be a string.")
    lowered = html.unescape(text).lower()
    letters_only = _NON_LETTERS.sub(" ", lowered)
    words = [w for w in letters_only.split() if w not in STOP_WORDS]
    return " ".join(words)


def tokenize(text: str) -> list[str]:
    """Split cleaned text into words.

    Args:
        text: raw or cleaned text.
    Returns:
        list of words from clean_text(text).
    Complexity: O(k) for k characters.
    """
    return clean_text(text).split()


def _make_vectorizer():
    """Build an unfitted TF-IDF vectoriser that uses our tokenizer.

    Returns:
        a scikit-learn TfidfVectorizer.
    Complexity: O(1).
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    return TfidfVectorizer(tokenizer=tokenize, preprocessor=None,
                           lowercase=False, token_pattern=None)


def fit_vectorizer(train_texts: list[str]):
    """Fit a TF-IDF vectoriser on the training texts only.

    Args:
        train_texts: raw training questions.
    Returns:
        (vectorizer, X_train) where X_train is a sparse matrix.
    Raises:
        ValidationError: if train_texts is empty or has no usable words.
    Complexity: O(N) for N words in all training texts.
    """
    if not train_texts:
        raise ValidationError("Need at least one training text.")
    vectorizer = _make_vectorizer()
    try:
        x_train = vectorizer.fit_transform(train_texts)
    except ValueError as err:  # sklearn: empty vocabulary
        raise ValidationError("Training texts contain no usable words.") from err
    return vectorizer, x_train


def transform_texts(vectorizer, texts: list[str]):
    """Turn new texts into TF-IDF vectors with an already fitted vectoriser.

    Args:
        vectorizer: from fit_vectorizer().
        texts: raw texts (for example the test questions).
    Returns:
        sparse matrix with one row per text.
    Complexity: O(N) for N words.
    """
    if not texts:      # sklearn refuses an empty list; return 0 rows instead
        from scipy.sparse import csr_matrix
        return csr_matrix((0, len(vectorizer.vocabulary_)))
    return vectorizer.transform(texts)


def search(query: str, texts: list[str], top_k: int = 5) -> list[tuple]:
    """Rank texts by TF-IDF cosine similarity to a query.

    Args:
        query: words typed by the user.
        texts: the questions or notes to search.
        top_k: how many results to return.
    Returns:
        [(index, score), ...], best match first, only scores above 0.
    Raises:
        ValidationError: if query is empty or top_k < 1.
    Complexity: O(n * v) for n texts and v vocabulary size.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValidationError("Search query cannot be empty.")
    if not isinstance(top_k, int) or top_k < 1:
        raise ValidationError("top_k must be at least 1.")
    if not texts:
        return []
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer, matrix = fit_vectorizer(texts)
    scores = cosine_similarity(transform_texts(vectorizer, [query]), matrix)[0]
    ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
    return [(i, float(s)) for i, s in ranked[:top_k] if s > 0]
