# ALPHA LMS

**Learning Management System · Programming for AI semester project**

ALPHA LMS is a Python console application for a small class. Students read notes, take quizzes, practise with live questions, submit assignments and get revision tips for weak topics. Teachers mark work, read Pandas class reports and get a topic suggestion for new quiz questions from a small classifier. Admins create accounts and enroll students. Everything runs from the terminal on local files, with fictional demonstration data only. The code uses NumPy, Pandas, Matplotlib, Seaborn and scikit-learn.

## Team

| Team member | Roll number | GitHub | What they built |
| --- | --- | --- | --- |
| Ashbar Hussain (group leader) | 25k-0028 | [@AshbarHussain25k0028](https://github.com/AshbarHussain25k0028) | Repo layout and sample data, user roles, JSON/CSV storage, assignments and marking, admin menu, Pandas class report and the Matplotlib/Seaborn charts. |
| Muhammad Mudassir | 25k-0153 | [@k250153-sudo](https://github.com/k250153-sudo) | Custom exceptions and validated input, courses and quizzes, role menus and revision tips, Open Trivia DB client with offline cache, NumPy score matrix, TF-IDF text features and the topic classifier. |

**Course:** AL-2001 · Programming for Artificial Intelligence (Laboratory) · Section BAI-3A · Fall 2026

## Features

- Three roles (student, teacher, admin) with separate menus and permission checks.
- Courses, notes and enrollment (a set, so no duplicates).
- Multiple-choice quizzes graded per topic, with rule-based revision tips that point to the matching notes.
- Practice questions from Open Trivia DB, saved to a local cache so they work offline.
- Assignments with deadlines, late flag, teacher marking (0 to maximum) and feedback.
- NumPy score matrix (students by quizzes) with missing attempts kept as NaN, percentages and averages without element loops.
- Pandas class report: cleaning, groupby by course and topic, merge, and a list of students needing attention.
- Four labelled charts saved to `outputs/figures/`: quiz averages line, assignment completion bar, score histogram and a topic heatmap.
- Text cleaning and TF-IDF question search.
- Question-topic classifier (Computers, History, Mathematics, Science & Nature): Naive Bayes against Logistic Regression and a keyword baseline on the same split, with 5-fold cross-validation. Test accuracy: baseline 0.54, Naive Bayes 0.77, Logistic Regression 0.76. Results are in `outputs/results/`.
- Safe saving (temporary file, then replace), custom exceptions and 377 pytest tests.

## Known limitations

- Login is by user ID only, with no password. It is a classroom demo, not real authentication.
- One user at a time, with data in local JSON and CSV files (no database, no web or GUI).
- The sample data is small and fictional.
- Open Trivia DB has only about 60 multiple-choice Mathematics questions, so the classifier is weakest on Mathematics. It was trained on trivia questions, so its topic suggestions on real course questions may be wrong. It only suggests; the teacher decides.
- Practice questions are not saved to a student's progress.
- Quiz questions are written in the data files. There is no screen for creating quizzes, and the teacher-approval step for API questions was not built.
- The requirement to "attach scanned notes" from the proposal was dropped: we chose the text track instead of image processing.

## Data source

Practice questions and the classifier's training data come from the free [Open Trivia DB](https://opentdb.com) (https://opentdb.com), whose questions are licensed CC BY-SA 4.0. A saved copy is in `data/raw/opentdb_cache.json`. All users, courses, quizzes, attempts and submissions in `data/raw/` are fictional.

## Getting started

You need **Python 3.11** (3.10 or newer should also work) and a terminal. All commands are run from the repository folder.

**1. Get the code**

```bash
git clone https://github.com/AshbarHussain25k0028/PAI.git
cd PAI
```

**2. Create a virtual environment and install the libraries**

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. Run the app**

```bash
python src/main.py
```

Log in by typing a user ID. The sample data is fictional:

| User ID | Role | What to try |
| --- | --- | --- |
| `S01` – `S08` | Student | My courses and materials, Take a quiz, Practice questions (Open Trivia DB, works offline from the cache), My assignments (see marks, submit), My progress and revision tips |
| `T01`, `T02` | Teacher | My courses and materials, Quiz results, Mark submissions, Class report (Pandas: averages by course and topic, one row per student, who needs attention), Suggest topic for my question (classifier advice; the teacher decides) |
| `A01` | Admin | List accounts, Create an account, Enroll a student, Save data |

Choose a menu line by its number. "Log out" returns to the login prompt; type `Q` there to quit.

**4. Where the data is saved**

The first run reads the sample data from `data/raw/`. Every change (new accounts, enrollments, quiz attempts, submissions, marks) is saved to `data/processed/` when you quit, or straight away with the admin's "Save data". Later runs read `data/processed/`. To start again from the sample data, delete the files in `data/processed/` (keep `.gitkeep`).

Practice questions come from the free [Open Trivia DB](https://opentdb.com) API (no key needed). A copy is saved in `data/raw/opentdb_cache.json`, so practice still works with no internet. To refresh the copy (it waits 5 seconds between calls, so it takes a few minutes):

```bash
python src/question_api.py
```

**5. Run the tests**

```bash
python -m pytest -q
```

## Documentation

[Design document](docs/DESIGN.md) (program flow, data structures, algorithms, complexity, viva questions) · [module interfaces](docs/INTERFACES.md) · [proposal](docs/proposal.md) · [roadmap](ROADMAP.md) · [contributing guide](CONTRIBUTING.md)

## Responsible use

Only fictional demonstration data is used. Real student identities, grades, submissions, credentials and API keys must not be committed to this public repository. Role and enrollment checks limit what each user sees. Revision tips support practice and do not judge a student's ability. Predicted topic labels can be corrected, and teachers keep control of assessment.
