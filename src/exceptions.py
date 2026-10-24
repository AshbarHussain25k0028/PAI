"""Custom exceptions for ALPHA LMS.

Owner: Muhammad Mudassir (Part 2)
Lab concept: Lab 06, custom exception classes.

Every error the LMS raises on purpose is a subclass of LMSError. The menus can
then catch LMSError in one place and show a friendly message, while Python's
own errors (bugs) still show up during development.

INTERFACE STUB (Part 1): the class names below are agreed. Part 2 adds the
messages and any extra attributes.
"""


class LMSError(Exception):
    """Base class for every error raised on purpose by ALPHA LMS."""


class ValidationError(LMSError):
    """A value typed by the user, or read from a file, is not valid.

    Example: a mark of 15 when the maximum is 10, or a date like "2026-13-40".
    """


class NotFoundError(LMSError):
    """An ID (user, course, quiz, assignment ...) does not exist."""


class DuplicateError(LMSError):
    """Something with the same ID or key already exists."""


class PermissionDeniedError(LMSError):
    """The logged-in user is not allowed to do this action."""


class DataFileError(LMSError):
    """A data file is missing, unreadable or badly formatted."""


class APIUnavailableError(LMSError):
    """The online question API could not be reached or sent a bad reply."""
