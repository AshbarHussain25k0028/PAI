# ALPHA LMS

**Learning Management System · Programming for AI semester project**

Notes in one chat, deadlines in another, and the assignment somehow missing? ALPHA LMS aims to bring learning resources, assignments, quizzes, and progress into one place.

ALPHA LMS is a proposed **Python console application** for a small school or college class. Teachers will organize learning activities, students will track their work, and revision suggestions will point them toward topics worth another look.

> **Project status: proposal and planning.** Application implementation has not started. The features below describe the intended scope; they are not completed features or measured results.

## What we plan to build

| Area | Planned functionality |
| --- | --- |
| Accounts and roles | Separate student, teacher, and administrator menus, with enrollment and permission checks. |
| Courses and materials | Organize courses and share teacher-provided notes and files. |
| Assignments | Set deadlines, record submissions, and provide teacher-entered marks and feedback. |
| Quizzes | Run teacher-approved multiple-choice quizzes and record attempts and topic-level results. |
| Progress | Show completed and missing work, quiz results, and useful charts. |
| Revision suggestions | Recommend relevant notes and practice topics using quiz mistakes and simple rules. |

The first version will serve **one class or department**, using local files. It will use resources already available, such as class lists, notes, questions, and assignment files. Extra hardware and paid AI services will not be required for the core application.

Live video classes, fee payments, a public web portal, and institution-wide deployment are outside the initial scope. Teachers will retain control of final marks.

## Where AI fits

We want the AI features to solve specific learning problems, rather than simply attach an AI label to ordinary record management.

| Feature | Proposed approach | Development stage |
| --- | --- | --- |
| Revision suggestions | Match missed quiz topics to relevant notes and practice. This is a rule-based recommendation method and needs no model training. | Planned core feature |
| Smart notes search | Clean text and use TF-IDF to rank passages relevant to a student's query. | Tentative extension after NLP lessons |
| Automatic subject tagging | Train a small classifier on notes labelled by subject or topic; compare it with a keyword baseline. | Tentative extension after ML and NLP lessons |
| Scanned-note preprocessing | Explore resizing, colour conversion, and normalization with OpenCV. This alone will not recognize handwriting or extract text. | Optional extension after image-processing lessons |

**Topics after Week 9 are yet to be studied in the proposal's learning plan. We will try to incorporate suitable concepts as we learn them and assess their feasibility. These are planned attempts, not guaranteed features.**

If we develop a classifier, we will evaluate it using held-out material, fit text vectorization on training data only, and report the results actually obtained. Search quality will be checked against relevant passages. No trained model, accuracy score, or AI-generated grading system is claimed at this stage.

## Course concepts

The foundation follows **Labs 01–09** of Programming for Artificial Intelligence:

| Concepts | Intended use |
| --- | --- |
| Python basics and control flow | Menus, validation, loops, and list/dictionary comprehensions. |
| Collections and functions | Course records, enrollments, reusable functions, scope, default arguments, `zip`, `enumerate`, `map`, `filter`, and `lambda`. |
| Object-oriented programming | A shared `User` class, student/teacher roles, courses, assignments, quizzes, encapsulation, inheritance, and overriding. |
| Files, exceptions, and APIs | TXT/CSV/JSON storage, recovery from errors, and an optional supplementary question-bank API using `requests`. |
| NumPy | Array manipulation, broadcasting, vectorized calculations, and comparisons with loops. |
| Pandas | Loading, cleaning, filtering, transforming, grouping, and merging learning records. |
| Matplotlib and Seaborn | Progress trends, completion bars, score histograms, scatter plots, and topic-level summaries. |

Later lessons may support train/test splitting, model comparison and cross-validation, text processing, optional image preprocessing, and a stronger documentation and ethical review. See the [roadmap](ROADMAP.md) for the proposed sequence.

## Proposed technology

- **Language:** Python 3
- **Interface:** console menus
- **Storage:** local TXT, CSV, JSON, and managed material/submission folders
- **Analysis:** NumPy and Pandas
- **Visualization:** Matplotlib and Seaborn; Jupyter Notebooks for exploration
- **Optional API integration:** `requests`
- **Possible later additions:** scikit-learn and OpenCV, after the corresponding course sessions

Dependency versions and the final module structure will be documented when implementation begins.

## Getting started

This repository currently contains the project overview, contribution guidance, and development roadmap. **There is no runnable application yet.**

Installation commands, a dependency file, demonstration accounts, safe example data, and the actual entry point will be added with the first working version. Until then, start with:

- [Development roadmap](ROADMAP.md)
- [Contributing guide](CONTRIBUTING.md)
- [Questions and suggestions](https://github.com/AshbarHussain25k0028/PAI/issues)

## Data and responsible use

We will begin with fictional demonstration accounts and material we have permission to use. Real student identities, grades, submissions, credentials, and API keys must not be committed to this public repository.

The intended application will check role and enrollment permissions. Revision suggestions will support practice, not judge a student's ability. Predicted subject labels will be correctable, and teachers will retain control over assessment.

## Team and course

| Team member | GitHub |
| --- | --- |
| Ashbar Hussain | [@AshbarHussain25k0028](https://github.com/AshbarHussain25k0028) |
| Muhammad Mudassir | — |

**Course:** AL-2001 · Programming for Artificial Intelligence (Laboratory)  
**Section:** BAI-3A  
**Session:** Fall 2026

Individual responsibilities and contributions will be recorded as development progresses.
