# Contributing to ALPHA LMS

ALPHA LMS is an academic project in the proposal stage. Contributions should help build the small, understandable LMS described in the [README](README.md) and [roadmap](ROADMAP.md).

## Before starting

1. Discuss the proposed change in an issue or with the project team.
2. Keep the first version focused on one class or department.
3. Distinguish a current implementation task from a tentative later-course AI experiment.
4. Agree on ownership so that individual contributions can be explained during the viva.

## Making a change

- Work on a focused branch with a descriptive name.
- Keep functions and classes small, readable, and documented.
- Follow the project's existing style once implementation begins.
- Explain the problem, the change, and how it was checked in the pull request.
- Add meaningful checks for new behaviour, especially role permissions, data integrity, and calculations.
- Update the README or roadmap when behaviour or project status changes.

Do not add guessed installation commands, fabricated performance results, or completed-feature claims for code that does not exist.

## Data and credentials

- Use fictional accounts and non-sensitive demonstration data.
- Do not commit real student names, grades, submissions, private class lists, passwords, API keys, or local configuration secrets.
- Only include course material you have permission to share.
- Keep generated local records and submissions out of version control; the `.gitignore` provides initial safeguards, not a substitute for reviewing a commit.

## AI-related work

- Keep rule-based revision suggestions clearly identified as rule-based.
- Treat ML/NLP/image-processing work as conditional until it is learned, implemented, and evaluated.
- Keep training and evaluation material separate; fit preprocessing on training data only.
- Report actual metrics and limitations when experiments are completed.
- Keep teacher control over final marks and make automated subject tags correctable.

No public student dataset, trained model, contributor work split, or production deployment is established by this repository's initial documentation.
