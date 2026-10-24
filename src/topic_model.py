"""Question-topic classifier: Naive Bayes vs Logistic Regression.

Owner: Muhammad Mudassir (Part 14)
Lab concepts: Lab 10 (train/test split), Lab 11 (comparing two models,
cross-validation).

How it works
------------
The cached Open Trivia DB questions are labelled with one of 4 categories
(Computers, Mathematics, Science & Nature, History). Both models use the
same train_test_split(test_size=0.25, random_state=42, stratify=y), and the
TF-IDF features from text_features.py. A keyword baseline shows how much the
models add. Metrics and the confusion matrix go to outputs/results/.

INTERFACE STUB (Part 1): bodies are written in Part 14.
"""

from __future__ import annotations

from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "outputs" / "results"
TEST_SIZE = 0.25
RANDOM_STATE = 42


def load_dataset(cache: dict) -> tuple[list[str], list[str]]:
    """Turn the API cache into texts and labels.

    Args:
        cache: {category_name: [question dicts]} from question_api.
    Returns:
        (texts, labels), two lists of the same length.
    Raises:
        ValidationError: if a category has no questions.
    Complexity: O(q) for q questions.
    """
    raise NotImplementedError("Part 14")


def split_data(texts: list[str], labels: list[str]) -> tuple:
    """Stratified train/test split with the agreed settings.

    Args:
        texts: question texts.
        labels: their categories.
    Returns:
        (X_train, X_test, y_train, y_test).
    Raises:
        ValidationError: if the lists differ in length or are too small.
    Complexity: O(q).
    """
    raise NotImplementedError("Part 14")


def keyword_baseline(texts: list[str], keywords: dict) -> list[str]:
    """Predict a category by counting keyword hits (no learning).

    Args:
        texts: question texts.
        keywords: {category: set of keywords}.
    Returns:
        predicted category for each text (most hits wins).
    Complexity: O(q * w) for q texts of w words.
    """
    raise NotImplementedError("Part 14")


def train_models(X_train, y_train) -> dict:
    """Fit MultinomialNB and LogisticRegression on the same training data.

    Args:
        X_train: TF-IDF training matrix.
        y_train: training labels.
    Returns:
        {"naive_bayes": model, "logistic_regression": model}.
    Complexity: depends on the model; about O(n * v) for n rows, v words.
    """
    raise NotImplementedError("Part 14")


def evaluate(model, X_test, y_test) -> dict:
    """Score one model on the held-out test set.

    Args:
        model: a fitted classifier.
        X_test: TF-IDF test matrix.
        y_test: true labels.
    Returns:
        {"accuracy": float, "report": str, "confusion": list of lists}.
    Complexity: O(n * v).
    """
    raise NotImplementedError("Part 14")


def cross_validate(texts: list[str], labels: list[str], folds: int = 5) -> dict:
    """5-fold cross-validation for both models (TF-IDF inside a Pipeline,
    so each fold fits it on its own training part).

    Args:
        texts: question texts.
        labels: their categories.
        folds: number of folds.
    Returns:
        {model_name: (mean_accuracy, std_accuracy)}.
    Raises:
        ValidationError: if folds < 2.
    Complexity: O(folds * training cost).
    """
    raise NotImplementedError("Part 14")


def save_results(results: dict, folder=None) -> Path:
    """Write metrics and confusion matrices to outputs/results/.

    Args:
        results: output of evaluate() and cross_validate() per model.
        folder: defaults to RESULTS_DIR.
    Returns:
        the Path of the saved metrics file.
    Raises:
        DataFileError: if the file cannot be written.
    Complexity: O(1) for a fixed number of models.
    """
    raise NotImplementedError("Part 14")


def suggest_topic(model, vectorizer, question_text: str) -> str:
    """Suggest a category for a new question typed by a teacher.

    Args:
        model: the chosen fitted classifier.
        vectorizer: the fitted TF-IDF vectoriser.
        question_text: the new question.
    Returns:
        the predicted category name (the teacher can change it).
    Raises:
        ValidationError: if question_text is empty.
    Complexity: O(w) for w words.
    """
    raise NotImplementedError("Part 14")
