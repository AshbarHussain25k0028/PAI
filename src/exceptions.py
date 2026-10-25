"""Custom exceptions for ALPHA LMS.

Owner: Muhammad Mudassir (Part 2)
Lab concept: Lab 06, custom exception classes.

Every error the LMS raises on purpose is a subclass of LMSError. The menus can
then catch LMSError in one place and show a friendly message, while Python's
own errors (bugs) still show up during development.

Each class has a default_message, so `raise NotFoundError()` still prints
something useful, and a custom message can be passed when we know more,
for example `raise NotFoundError("No course with ID C999")`.
"""


class LMSError(Exception):
    """Base class for every error raised on purpose by ALPHA LMS.

    Attributes:
        message (str): the text shown to the user.
    """

    default_message = "Something went wrong in ALPHA LMS."

    def __init__(self, message: str = ""):
        """Store the message (or the class default if none is given).

        Args:
            message: what went wrong, in plain words.
        Complexity: O(1).
        """
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return the message so print(error) shows it.

        Returns:
            the message text.
        Complexity: O(1).
        """
        return self.message


class ValidationError(LMSError):
    """A value typed by the user, or read from a file, is not valid.

    Example: a mark of 15 when the maximum is 10, or a date like "2026-13-40".
    """

    default_message = "That value is not valid."


class NotFoundError(LMSError):
    """An ID (user, course, quiz, assignment ...) does not exist."""

    default_message = "No record with that ID was found."


class DuplicateError(LMSError):
    """Something with the same ID or key already exists."""

    default_message = "A record with that ID already exists."


class PermissionDeniedError(LMSError):
    """The logged-in user is not allowed to do this action."""

    default_message = "You are not allowed to do that."


class DataFileError(LMSError):
    """A data file is missing, unreadable or badly formatted."""

    default_message = "A data file is missing or could not be read."


class APIUnavailableError(LMSError):
    """The online question API could not be reached or sent a bad reply."""

    default_message = "The question service is not available right now."
