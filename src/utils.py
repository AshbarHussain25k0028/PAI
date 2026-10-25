"""Small helpers for safe console input and IDs.

Owner: Muhammad Mudassir (Part 2)
Lab concepts: Labs 01-02 (type conversion, loops, validated input), Lab 04 (functions).

The ask_* functions loop until the user types something valid, so the rest of
the program never has to deal with bad keyboard input.
"""

from __future__ import annotations

from datetime import datetime

from exceptions import ValidationError

DATE_FORMAT = "%Y-%m-%d %H:%M"   # every date in the data files uses this format


def ask_int(prompt: str, low: int, high: int) -> int:
    """Keep asking until the user types a whole number between low and high.

    Args:
        prompt: text shown to the user.
        low, high: smallest and largest allowed value (both included).
    Returns:
        the number the user typed, as an int.
    Complexity: O(1) per attempt.
    """
    while True:
        text = input(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            print(f"Please type a whole number from {low} to {high}.")
            continue
        if low <= number <= high:
            return number
        print(f"Please type a number from {low} to {high}.")


def ask_choice(title: str, options: list[str]) -> int:
    """Print a numbered menu and return the chosen position (starting at 1).

    Args:
        title: heading printed above the menu.
        options: menu lines, in display order.
    Returns:
        an int from 1 to len(options).
    Raises:
        ValidationError: if options is empty (there is nothing to choose).
    Complexity: O(n) to print n options.
    """
    if not options:
        raise ValidationError("A menu needs at least one option.")
    print(f"\n{title}")
    print("-" * len(title))
    for number, line in enumerate(options, start=1):
        print(f"  {number}. {line}")
    return ask_int("Choose an option: ", 1, len(options))


def ask_text(prompt: str, allow_empty: bool = False) -> str:
    """Ask for a line of text and strip the spaces around it.

    Args:
        prompt: text shown to the user.
        allow_empty: if False, keep asking until something is typed.
    Returns:
        the cleaned text.
    Complexity: O(k) for k characters.
    """
    while True:
        text = input(prompt).strip()
        if text or allow_empty:
            return text
        print("This cannot be empty, please type something.")


def parse_datetime(text: str):
    """Turn "YYYY-MM-DD HH:MM" into a datetime object.

    Args:
        text: the date as written in a file or typed by the user.
    Returns:
        datetime.datetime
    Raises:
        ValidationError: if the text is not a real date in that format.
    Complexity: O(1).
    """
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT)
    except (ValueError, AttributeError) as error:
        raise ValidationError(
            f"'{text}' is not a valid date. Use YYYY-MM-DD HH:MM, "
            "for example 2026-11-05 23:00."
        ) from error


def format_datetime(moment) -> str:
    """Turn a datetime back into "YYYY-MM-DD HH:MM" for saving.

    Args:
        moment: a datetime.datetime object.
    Returns:
        the date as text in DATE_FORMAT.
    Complexity: O(1).
    """
    return moment.strftime(DATE_FORMAT)


def make_id(prefix: str, existing_ids) -> str:
    """Create the next free ID, e.g. make_id("S", {"S01", "S02"}) -> "S03".

    Only IDs that are the prefix followed by digits count, so "AS01" does not
    affect make_id("A", ...).

    Args:
        prefix: a short prefix such as "S", "T", "C", "Q", "M", "AS".
        existing_ids: set or dict keys of IDs already used.
    Returns:
        a new ID that is not in existing_ids.
    Complexity: O(n) for n existing IDs.
    """
    numbers = [int(old[len(prefix):]) for old in existing_ids
               if old.startswith(prefix) and old[len(prefix):].isdigit()]
    next_number = max(numbers, default=0) + 1
    return f"{prefix}{next_number:02d}"


def require_text(value, field: str) -> str:
    """Check that a value is a non-empty string and return it stripped.

    Helper added in Part 2, used by the from_dict / __init__ checks.

    Args:
        value: the value to check (may be None when a CSV column is missing).
        field: the field name, used in the error message.
    Returns:
        the value without surrounding spaces.
    Raises:
        ValidationError: if the value is missing, not text, or empty.
    Complexity: O(k) for k characters.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{field}' must not be empty.")
    return value.strip()
