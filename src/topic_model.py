"""Question-topic classifier: Naive Bayes vs Logistic Regression.

Owner: Muhammad Mudassir (Part 14)
Lab concepts: Lab 10 (train/test split), Lab 11 (comparing two models,
cross-validation).

How it works
------------
The cached Open Trivia DB questions are labelled with one of 4 categories
(Computers, Mathematics, Science & Nature, History). Both models use the
same train_test_split(test_size=0.25, random_state=42, stratify=y), and the
TF-IDF features from text_features.py (fitted on the training part only). A
keyword baseline shows how much the models add. Metrics and the confusion
matrix go to outputs/results/.

Key data structures: the cache is a dict {category: [questions]}; the
keyword baseline uses a dict {category: set of keywords} (set lookup is
O(1)); the fitted models sit in a dict {name: model}, so both are handled by
the same code. The teacher menu item "Suggest topic for my question" uses
the model that scored better on the test set.

Run the whole experiment from the repo root with:  python src/topic_model.py
"""

from __future__ import annotations

import json
from pathlib import Path

from exceptions import DataFileError, ValidationError
from text_features import _make_vectorizer, fit_vectorizer, tokenize, transform_texts

RESULTS_DIR = Path(__file__).resolve().parent.parent / "outputs" / "results"
TEST_SIZE = 0.25
RANDOM_STATE = 42
MODEL_NAMES = ("naive_bayes", "logistic_regression")
MIN_TEXTS = 8    # fewer questions than this cannot be split sensibly

# Hand-picked words for the baseline (a set per category: O(1) membership).
KEYWORDS = {
    "Computers": {"computer", "software", "programming", "windows", "linux",
                  "internet", "cpu", "processor", "keyboard", "html", "java",
                  "python", "intel", "amd", "google", "data", "web", "file",
                  "code", "microsoft", "apple", "digital", "network", "bit"},
    "Mathematics": {"number", "equation", "angle", "triangle", "prime",
                    "algebra", "geometry", "sum", "square", "root", "integer",
                    "calculus", "formula", "theorem", "mathematical", "pi",
                    "fraction", "graph", "digits", "value"},
    "Science & Nature": {"animal", "species", "chemical", "element", "planet",
                         "biology", "atom", "cell", "gas", "plant", "energy",
                         "bird", "metal", "human", "body", "space", "earth",
                         "physics", "dna", "bone"},
    "History": {"war", "king", "queen", "emperor", "empire", "battle",
                "century", "president", "revolution", "ancient", "roman",
                "world", "born", "army", "treaty", "napoleon", "died",
                "dynasty", "nation", "independence"},
}


def load_dataset(cache: dict) -> tuple[list[str], list[str]]:
    """Turn the API cache into texts and labels.

    Args:
        cache: {category_name: [question dicts]} from question_api.
    Returns:
        (texts, labels), two lists of the same length.
    Raises:
        ValidationError: if the cache is empty or a category has no questions.
    Complexity: O(q) for q questions.
    """
    if not isinstance(cache, dict) or not cache:
        raise ValidationError("There are no cached questions to learn from.")
    texts, labels = [], []
    for category, questions in cache.items():
        usable = [q["question"] for q in questions
                  if isinstance(q, dict) and q.get("question")]
        if not usable:
            raise ValidationError(f"The category {category} has no questions.")
        texts.extend(usable)
        labels.extend([category] * len(usable))
    return texts, labels


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
    from sklearn.model_selection import train_test_split

    if len(texts) != len(labels):
        raise ValidationError("Texts and labels must have the same length.")
    if len(texts) < MIN_TEXTS:
        raise ValidationError(f"Need at least {MIN_TEXTS} questions.")
    try:
        return train_test_split(texts, labels, test_size=TEST_SIZE,
                                random_state=RANDOM_STATE, stratify=labels)
    except ValueError as error:   # for example a category with 1 question
        raise ValidationError(f"Could not split the data: {error}") from error


def keyword_baseline(texts: list[str], keywords: dict) -> list[str]:
    """Predict a category by counting keyword hits (no learning).

    Args:
        texts: question texts.
        keywords: {category: set of keywords}.
    Returns:
        predicted category for each text (most hits wins; a tie goes to the
        category listed first).
    Raises:
        ValidationError: if keywords is empty.
    Complexity: O(q * w) for q texts of w words.
    """
    if not keywords:
        raise ValidationError("The baseline needs at least one category.")
    predictions = []
    for text in texts:
        words = tokenize(text)
        hits = {name: sum(word in word_set for word in words)
                for name, word_set in keywords.items()}
        predictions.append(max(hits, key=hits.get))   # max keeps the first tie
    return predictions


def _new_models() -> dict:
    """Build the two unfitted classifiers.

    Returns:
        {"naive_bayes": MultinomialNB, "logistic_regression": LogisticRegression}.
    Complexity: O(1).
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB

    return {"naive_bayes": MultinomialNB(),
            "logistic_regression": LogisticRegression(
                max_iter=1000, random_state=RANDOM_STATE)}


def train_models(X_train, y_train) -> dict:
    """Fit MultinomialNB and LogisticRegression on the same training data.

    Args:
        X_train: TF-IDF training matrix.
        y_train: training labels.
    Returns:
        {"naive_bayes": model, "logistic_regression": model}.
    Complexity: depends on the model; about O(n * v) for n rows, v words.
    """
    models = _new_models()
    for model in models.values():
        model.fit(X_train, y_train)
    return models


def _scores(y_true, y_pred, labels: list[str]) -> dict:
    """Accuracy, text report and confusion matrix for one set of predictions.

    Args:
        y_true: true labels.
        y_pred: predicted labels.
        labels: category names, in the order used for the matrix.
    Returns:
        {"accuracy": float, "report": str, "confusion": list of lists}.
    Complexity: O(n).
    """
    from sklearn.metrics import (accuracy_score, classification_report,
                                 confusion_matrix)

    return {"accuracy": float(accuracy_score(y_true, y_pred)),
            "report": classification_report(y_true, y_pred, labels=labels,
                                            zero_division=0),
            "confusion": confusion_matrix(y_true, y_pred,
                                          labels=labels).tolist()}


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
    return _scores(y_test, model.predict(X_test), sorted(set(y_test)))


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
        ValidationError: if folds < 2 or a category has fewer questions
            than folds.
    Complexity: O(folds * training cost).
    """
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import make_pipeline

    if not isinstance(folds, int) or folds < 2:
        raise ValidationError("Cross-validation needs at least 2 folds.")
    if min(labels.count(name) for name in set(labels)) < folds:
        raise ValidationError("Every category needs at least one question per fold.")
    splitter = StratifiedKFold(n_splits=folds, shuffle=True,
                               random_state=RANDOM_STATE)
    results = {}
    for name, model in _new_models().items():
        pipeline = make_pipeline(_make_vectorizer(), model)
        scores = cross_val_score(pipeline, texts, labels, cv=splitter)
        results[name] = (float(scores.mean()), float(scores.std()))
    return results


def _write_confusion_csv(path: Path, labels: list[str], matrix: list) -> None:
    """Write one confusion matrix as CSV (rows = true, columns = predicted).

    Args:
        path: destination file.
        labels: category names.
        matrix: list of lists of counts.
    Raises:
        OSError: if the file cannot be written (save_results catches it).
    Complexity: O(c^2) for c categories.
    """
    lines = ["true/predicted," + ",".join(f'"{name}"' for name in labels)]
    for name, row in zip(labels, matrix):
        lines.append(f'"{name}",' + ",".join(str(count) for count in row))
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def save_results(results: dict, folder=None) -> Path:
    """Write metrics and confusion matrices to outputs/results/.

    Args:
        results: {"labels": [...], "models": {name: {accuracy, report,
            confusion, cv_mean, cv_std}}, ...} from run_experiment().
        folder: defaults to RESULTS_DIR.
    Returns:
        the Path of the saved metrics file (topic_model_results.json).
    Raises:
        DataFileError: if the file cannot be written.
        ValidationError: if results has no "models" entry.
    Complexity: O(1) for a fixed number of models.
    """
    if not isinstance(results, dict) or "models" not in results:
        raise ValidationError("Results must contain a 'models' entry.")
    folder = Path(RESULTS_DIR if folder is None else folder)
    path = folder / "topic_model_results.json"
    try:
        folder.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=2)
        for name, scores in results["models"].items():
            _write_confusion_csv(folder / f"confusion_matrix_{name}.csv",
                                 results["labels"], scores["confusion"])
    except OSError as error:
        raise DataFileError("Could not save the model results.") from error
    return path


def suggest_topic(model, vectorizer, question_text: str) -> str:
    """Suggest a category for a new question typed by a teacher.

    Args:
        model: the chosen fitted classifier.
        vectorizer: the fitted TF-IDF vectoriser.
        question_text: the new question.
    Returns:
        the predicted category name (the teacher can change it).
    Raises:
        ValidationError: if question_text is empty or has no usable words.
    Complexity: O(w) for w words.
    """
    if not isinstance(question_text, str) or not question_text.strip():
        raise ValidationError("Type a question first.")
    if not tokenize(question_text):
        raise ValidationError("The question has no usable words.")
    vector = transform_texts(vectorizer, [question_text])
    return str(model.predict(vector)[0])


def run_experiment(cache: dict, folds: int = 5) -> dict:
    """Run the whole comparison on the same split and collect the numbers.

    Args:
        cache: {category_name: [question dicts]}.
        folds: folds for cross-validation.
    Returns:
        {"labels", "counts", "split", "baseline_accuracy", "models"}, where
        each model entry holds accuracy, report, confusion, cv_mean, cv_std.
        The fitted objects come back under "fitted" (not saved to JSON).
    Raises:
        ValidationError: see load_dataset, split_data, cross_validate.
    Complexity: O(folds * training cost).
    """
    texts, labels = load_dataset(cache)
    x_tr, x_te, y_tr, y_te = split_data(texts, labels)
    vectorizer, train_matrix = fit_vectorizer(x_tr)   # training texts only
    test_matrix = transform_texts(vectorizer, x_te)
    fitted = train_models(train_matrix, y_tr)
    models = {name: evaluate(m, test_matrix, y_te) for name, m in fitted.items()}
    for name, (mean, std) in cross_validate(texts, labels, folds).items():
        models[name].update(cv_mean=mean, cv_std=std)
    names = sorted(set(labels))
    baseline = _scores(y_te, keyword_baseline(x_te, KEYWORDS), names)
    return {"labels": names,
            "counts": {name: labels.count(name) for name in names},
            "split": {"test_size": TEST_SIZE, "random_state": RANDOM_STATE,
                      "train": len(x_tr), "test": len(x_te), "folds": folds},
            "baseline": baseline, "baseline_accuracy": baseline["accuracy"],
            "models": models,
            "fitted": {"models": fitted, "vectorizer": vectorizer}}


def best_model_name(results: dict) -> str:
    """Name of the model with the higher test accuracy (tie: cross-validation).

    Args:
        results: output of run_experiment().
    Returns:
        "naive_bayes" or "logistic_regression".
    Complexity: O(1).
    """
    models = results["models"]
    return max(MODEL_NAMES,
               key=lambda n: (models[n]["accuracy"], models[n]["cv_mean"]))


def train_best(cache: dict) -> tuple:
    """Train both models on the training split and return the better one.

    Used by the teacher menu: no cross-validation, so it is quick.

    Args:
        cache: {category_name: [question dicts]}.
    Returns:
        (model, vectorizer, model_name, test_accuracy).
    Raises:
        ValidationError: see load_dataset and split_data.
    Complexity: O(n * v) for n training rows, v words.
    """
    texts, labels = load_dataset(cache)
    x_tr, x_te, y_tr, y_te = split_data(texts, labels)
    vectorizer, train_matrix = fit_vectorizer(x_tr)
    test_matrix = transform_texts(vectorizer, x_te)
    fitted = train_models(train_matrix, y_tr)
    accuracy = {n: evaluate(m, test_matrix, y_te)["accuracy"]
                for n, m in fitted.items()}
    name = max(MODEL_NAMES, key=accuracy.get)
    return fitted[name], vectorizer, name, accuracy[name]


def print_comparison(results: dict) -> None:
    """Print the comparison table.

    Args:
        results: output of run_experiment().
    Complexity: O(1).
    """
    split = results["split"]
    print(f"Questions per category: {results['counts']}")
    print(f"Train {split['train']} / test {split['test']} "
          f"(test_size={split['test_size']}, random_state={split['random_state']})")
    print(f"{'Method':<22}{'Test acc.':>10}{'CV mean':>10}{'CV std':>9}")
    print(f"{'keyword baseline':<22}{results['baseline_accuracy']:>10.3f}"
          f"{'-':>10}{'-':>9}")
    for name in MODEL_NAMES:
        m = results["models"][name]
        print(f"{name:<22}{m['accuracy']:>10.3f}{m['cv_mean']:>10.3f}"
              f"{m['cv_std']:>9.3f}")
    print(f"Better on the test set: {best_model_name(results)}")


def main() -> None:
    """Load the cache, run the experiment, print and save the results.

    Complexity: O(folds * training cost).
    """
    from question_api import load_cache

    results = run_experiment(load_cache())
    print_comparison(results)
    saved = {key: value for key, value in results.items() if key != "fitted"}
    print(f"Saved to {save_results(saved)}")


if __name__ == "__main__":
    main()
