"""Smoke test: every module in src/ can be imported.

Owner: Ashbar Hussain (Part 1)
"""

import importlib

import pytest

MODULES = [
    "exceptions", "utils", "courses", "users", "quizzes", "assignments",
    "storage", "main", "question_api", "scores", "analysis", "charts",
    "text_features", "topic_model",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    """Each agreed module imports without errors.

    Args:
        name: module name inside src/.
    Complexity: O(1) per module.
    """
    assert importlib.import_module(name) is not None


def test_custom_exceptions_share_base():
    """Every custom error is a subclass of LMSError.

    Complexity: O(1).
    """
    exceptions = importlib.import_module("exceptions")
    for cls in (exceptions.ValidationError, exceptions.NotFoundError,
                exceptions.DuplicateError, exceptions.PermissionDeniedError,
                exceptions.DataFileError, exceptions.APIUnavailableError):
        assert issubclass(cls, exceptions.LMSError)
