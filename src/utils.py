"""Small helpers for safe console input and IDs.

Owner: Muhammad Mudassir (Part 2)
Lab concepts: Labs 01-02 (type conversion, loops, validated input), Lab 04 (functions).

INTERFACE STUB (Part 1): names, inputs, outputs and complexity are agreed.
Bodies are written in Part 2.
"""

from __future__ import annotations

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
    raise NotImplementedError("Part 2")


def ask_choice(title: str, options: list[str]) -> int:
    """Print a numbered menu and return the chosen position (starting at 1).

    Args:
        title: heading printed above the menu.
        options: menu lines, in display order.
    Returns:
        an int from 1 to len(options).
    Complexity: O(n) to print n options.
    """
    raise NotImplementedError("Part 2")


def ask_text(prompt: str, allow_empty: bool = False) -> str:
    """Ask for a line of text and strip the spaces around it.

    Args:
        prompt: text shown to the user.
        allow_empty: if False, keep asking until something is typed.
    Returns:
        the cleaned text.
    Complexity: O(k) for k characters.
    """
    raise NotImplementedError("Part 2")


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
    raise NotImplementedError("Part 2")


def format_datetime(moment) -> str:
    """Turn a datetime back into "YYYY-MM-DD HH:MM" for saving.

    Args:
        moment: a datetime.datetime object.
    Returns:
        the date as text in DATE_FORMAT.
    Complexity: O(1).
    """
    raise NotImplementedError("Part 2")


def make_id(prefix: str, existing_ids) -> str:
    """Create the next free ID, e.g. make_id("S", {"S01", "S02"}) -> "S03".

    Args:
        prefix: a short prefix such as "S", "T", "C", "Q", "M", "AS".
        existing_ids: set or dict keys of IDs already used.
    Returns:
        a new ID that is not in existing_ids.
    Complexity: O(n) for n existing IDs.
    """
    raise NotImplementedError("Part 2")
