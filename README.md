# ALPHA LMS

**Learning Management System · Programming for AI semester project**

Notes in one chat, deadlines in another, and the assignment somehow missing? ALPHA LMS aims to bring learning resources, assignments, quizzes, and progress into one place.

ALPHA LMS is a proposed **Python console application** for a small school or college class. Teachers will organize learning activities, students will track their work, and revision suggestions will point them toward topics worth another look.

> **Project status: half-project release (v0.5).** The console app runs: login for three roles, courses and notes, quizzes with topic results and revision tips, assignments with submission and marking, account and enrollment management, and saving to local files. The analysis, charts, question API and AI parts listed below are still planned.

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
| `T01`, `T02` | Teacher | My courses and materials, Quiz results, Mark submissions, Class report (Pandas: averages by course and topic, one row per student, who needs attention) |
| `A01` | Admin | List accounts, Create an account, Enroll a student, Save data |

Choose a menu line by its number. "Log out" returns to the login prompt; type `Q` there to quit.

**4. Where the data is saved**

The first run reads the sample data from `data/raw/`. Every change (new accounts, enrollments, quiz attempts, submissions, marks) is saved to `data/processed/` when you quit, or straight away with the admin's "Save data". Later runs read `data/processed/`. To start again from the sample data, delete the files in `data/processed/` (keep `.gitkeep`).

Practice questions come from the free [Open Trivia DB](https://opentdb.com) API (no key needed; questions are licensed CC BY-SA 4.0). A copy is saved in `data/raw/opentdb_cache.json`, so practice still works with no internet. To refresh the copy (it waits 5 seconds between calls, so it takes a few minutes):

```bash
python src/question_api.py
```

**5. Run the tests**

```bash
python -m pytest -q
```

More detail: [module interfaces](docs/INTERFACES.md) · [proposal](docs/proposal.md) · [roadmap](ROADMAP.md) · [contributing guide](CONTRIBUTING.md)

## Data and responsible use

We will begin with fictional demonstration accounts and material we have permission to use. Real student identities, grades, submissions, credentials, and API keys must not be committed to this public repository.

The intended application will check role and enrollment permissions. Revision suggestions will support practice, not judge a student's ability. Predicted subject labels will be correctable, and teachers will retain control over assessment.

## Team and course

| Team member | Roll number | GitHub |
| --- | --- | --- |
| Ashbar Hussain | 25k-0028 | [@AshbarHussain25k0028](https://github.com/AshbarHussain25k0028) |
| Muhammad Mudassir | 25k-0153 | [@k250153-sudo](https://github.com/k250153-sudo) |

**Course:** AL-2001 · Programming for Artificial Intelligence (Laboratory)  
**Section:** BAI-3A  
**Session:** Fall 2026

Individual responsibilities and contributions will be recorded as development progresses.
