"""ALPHA LMS console entry point. Run from the repo root:

    python src/main.py

Owner: Muhammad Mudassir (Part 7: login and role menus),
       Ashbar Hussain (Part 1: this starting version, Part 8: admin menu).

Part 1 version: prints a banner and says the features are coming soon, so
the program already runs. Part 7 adds login and the role menu loop, where
every role is handled with the same calls (polymorphism).
"""

from __future__ import annotations

BANNER = "ALPHA LMS - Learning Management System"


def show_banner() -> None:
    """Print the program title between two lines.

    Complexity: O(1).
    """
    line = "=" * len(BANNER)
    print(line)
    print(BANNER)
    print(line)


def run() -> None:
    """Start the program.

    Part 1 only shows the banner. Part 7 replaces the message with login and
    the role menu loop.

    Complexity: O(1).
    """
    show_banner()
    print("Features coming soon: login, courses, quizzes and assignments.")


if __name__ == "__main__":
    run()
