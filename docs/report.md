# ALPHA LMS: Project Report

**FAST — National University of Computer and Emerging Sciences, Karachi Campus**
**AL-2001 · Programming for Artificial Intelligence (Laboratory) · Fall 2026 · BAI-3A**
Lab instructor: Miss Khadeeja Ashraf

| | Student name | Roll number | GitHub |
|---|---|---|---|
| Member 1 (group leader) | Ashbar Hussain | 25k-0028 | AshbarHussain25k0028 |
| Member 2 | Muhammad Mudassir | 25k-0153 | k250153-sudo |

Repository: https://github.com/AshbarHussain25k0028/PAI

## Declaration and contribution statement

This report describes what we actually built. Every number in it comes from the code in this repository and from the files in `outputs/results/`. The full table of who wrote which part is in Chapter 8. External code, data and libraries are listed in Chapter 5 (data) and Appendix B (references).

## 1. Introduction

### 1.1 Overview
ALPHA LMS is a Python console Learning Management System for a small class. It keeps courses, teacher notes, quizzes, assignments, submissions and marks in one program. Three roles use it: students (take quizzes, submit work, see progress and revision tips), teachers (see results, mark submissions, read a class report) and an administrator (create accounts, enrol students). A small classifier helps a teacher tag a new question with its topic.

### 1.2 Objectives and scope
We aimed to (1) organise learning records in one workflow, (2) show progress with tables and charts, (3) suggest what to revise using simple rules, and (4) add one honest machine-learning component. The app is console-only and stores data in local files. Video classes, fees, a web portal and deployment are out of scope.

## 2. Problem statement and requirements

Notes, deadlines and marks are often spread over chats and spreadsheets. We wanted one place where a student sees courses and upcoming work and a teacher sees submissions and results. The project must also cover Labs 01–14 (guidelines, section 3). The table shows where each requirement lives.

| Lab | Requirement | Where it is |
|---|---|---|
| 01–02 | Validated input, loops, comprehensions | `utils.py` (`ask_int`, `ask_choice`, `ask_text`, `parse_datetime`), menus in `main.py` |
| 03 | list, tuple, dict, set, each justified | `courses.py` (set, list), `quizzes.py` (tuple, list, dict), `assignments.py` (tuple key), `storage.py` (dicts) |
| 04 | Functions, `lambda` with `sorted` | `quizzes.py` `suggest_revision`, `assignments.py` pending list, `admin.py` |
| 05 | Classes, encapsulation, inheritance, overriding, polymorphism, ABC | `users.py` (`User` ABC, `Student`, `Teacher`, `Admin`), `assignments.py` (`marks` property) |
| 06 | TXT/CSV/JSON, specific `except`, custom exception, API with cache | `storage.py`, `exceptions.py`, `question_api.py` |
| 07 | NumPy 2-D, mask, broadcasting, axis, no loops | `scores.py` |
| 08 | Pandas build, clean, filter, groupby, merge | `analysis.py` |
| 09 | Three or more labelled charts | `charts.py` (four charts) |
| 10–11 | Split, fitted model, two-model comparison, cross-validation | `topic_model.py` |
| 12 | Track A: own text cleaning + TF-IDF | `text_features.py` |
| 14 | Professional practice and ethics | docstrings everywhere, `README.md`, `requirements.txt`, `tests/`, section 7.3 |

We chose **Track A (text)**. Track B (images) is not used.

## 3. System design and architecture

### 3.1 Overall architecture
`main.py` shows a login prompt and then a role menu. Every role goes through the same calls (`user.menu_options()`, `user.can_view_student()`), so the menu loop does not care which role it holds. The menu calls the components below. `storage.DataStore` loads everything at start (from `data/processed/` if it exists, otherwise from `data/raw/`) and saves to `data/processed/`.

```
main.py (login + role menu)
  |-- users.py        roles (ABC User -> Student, Teacher, Admin)
  |-- courses.py      Course, Material
  |-- quizzes.py      Quiz, grading, revision suggestions
  |-- assignments.py  Assignment, Submission, marking
  |-- admin.py        accounts and enrolment
  |-- storage.py      JSON/CSV load and safe save, DataStore
  |-- question_api.py Open Trivia DB + offline cache
  |-- scores.py       NumPy score matrix
  |-- analysis.py     Pandas progress report
  |-- charts.py       Matplotlib / Seaborn figures
  |-- text_features.py  text cleaning + TF-IDF + search
  |-- topic_model.py  topic classifier (NB vs LogReg)
exceptions.py and utils.py are used by all modules.
```

### 3.2 Class design
`User` is an abstract base class (`abc.ABC`) with the abstract methods `menu_options()` and `can_view_student()`. `Student`, `Teacher` and `Admin` override both. The user id and name are read-only properties (encapsulation). `Course` holds the materials and enrolled students. `Quiz` holds its questions. `Assignment` has a `datetime` deadline. `Submission` keeps its marks in a protected attribute behind a property whose setter rejects values below 0 or above the maximum. `DataStore` owns the id → object dictionaries.

### 3.3 Choice of data structures

| Structure | Where | Why |
|---|---|---|
| `dict` id → object | `DataStore.users/courses/assignments/quizzes` | look up a record by id in O(1) |
| `set` of student ids | `Course.enrolled` | no duplicate enrolments, O(1) membership test |
| `list` | `Course.materials`, `Quiz.questions` | keeps display order |
| `tuple` | question records, submission key `(student_id, assignment_id)` | fixed record, can be a dict key |
| NumPy 2-D array | `scores.score_matrix()` | whole-table maths without loops |
| Pandas DataFrame | `analysis.build_progress_frame()` | labelled table for cleaning and groupby |

## 4. Implementation

### 4.1 Module overview
The source is 15 modules in `src/` (about 4,500 lines) plus 5 test files in `tests/` (about 1,900 lines). Every function has a docstring with Args, Returns, Raises and Complexity, and the functions are kept short. File access always uses `with`, every `requests` call has a `timeout`, and there is no bare `except`.

### 4.2 Lab coverage
See the table in Chapter 2. Each module's docstring names the lab it uses.

### 4.3 Key implementation details
- **Storage (`storage.py`).** JSON and CSV are loaded with specific `except` blocks (`FileNotFoundError`, `json.JSONDecodeError`, `csv.Error`, `OSError`) and re-raised as our `DataFileError`. A save writes a temporary file and then replaces the real one, so a failed write leaves the old data safe.
- **Quizzes (`quizzes.py`).** `grade_attempt()` returns the score and a dict `{topic: (correct, total)}`. `suggest_revision()` ranks weak topics with `sorted(key=lambda …)`, weakest first.
- **Assignments (`assignments.py`).** A late flag is computed from the deadline. The marks property protects the 0..max range.
- **Question API (`question_api.py`).** It asks Open Trivia DB for multiple-choice questions, checks the HTTP status and the API's `response_code`, waits the 5-second rate limit between calls, and saves the reply in `data/raw/opentdb_cache.json`. If the network is down it reads the cache. The cache holds 518 questions in four categories.
- **NumPy (`scores.py`).** `score_matrix()` builds a students × quizzes array with NaN for a quiz the student did not attempt. A boolean mask finds the missing cells, `to_percentages()` divides the whole array by the maximum scores by broadcasting, and the class and student averages use `sum(axis=…)` over the mask. There is no Python loop over elements.
- **Pandas (`analysis.py`).** Attempts and submissions become DataFrames. `clean_frame()` drops duplicates, trims and upper-cases ids, parses dates and turns blank marks into NaN. `course_summary()` and `topic_summary()` use `groupby`. `class_report()` merges the quiz and assignment tables on `student_id` (outer merge) so that a student with no attempts still appears.
- **Text (`text_features.py`).** `clean_text()` is our own code: HTML unescape, lower case, letters only, stop-word removal. The TF-IDF vectoriser is fitted on the training texts only. A cosine-similarity `search()` ranks stored questions.
- **Topic model (`topic_model.py`).** See Chapter 6.

## 5. Dataset

- **LMS sample data** (`data/raw/`): fictional only. 1 admin, 2 teachers, 8 students, 2 courses (C101 Programming for AI, C102 Data Science Basics), 7 notes files, 3 assignments, 17 quiz attempts and a few submissions (some unmarked, one late). Several students deliberately miss some quizzes so the missing-value handling is tested.
- **Question data:** [Open Trivia DB](https://opentdb.com), free, no key, licensed CC BY-SA 4.0. We cached 518 questions: Computers 149, History 156, Science & Nature 153, Mathematics 60 (Mathematics is smaller because the source has fewer questions in that category).
- No real student data, passwords or API keys are in the repository.

## 6. Results and analysis

### 6.1 Program output
Students and teachers see different menus. The teacher's "Class report" prints one row per student (quiz average, assignments submitted, missing work) and a list of students who need attention. The student's "My progress" prints per-topic results and the weakest topics first. Run `python src/main.py` and log in as `S01`, `T01` or `A01` to see them.

### 6.2 Visualisations
Charts are saved to `outputs/figures/` by `python src/charts.py`.

1. **Class average per quiz** (`quiz_averages.png`, line chart). C101's average rises slightly from about 69% to 72% across two quizzes, and C102's single quiz is about 71%. All averages are above the 60% pass line. With only three quizzes the trend is weak evidence.
2. **Assignment completion** (`assignment_completion.png`, bar chart). Submitted versus enrolled: AS01 5 of 8, AS02 1 of 8, AS03 3 of 5. AS02 has by far the lowest completion, so the teacher should follow it up.
3. **Distribution of quiz scores** (`score_histogram.png`, histogram). 17 attempts, mean 70.6%. The scores split into two groups (50–70% and 80–100%) with one weak attempt near 30–40%, so the mean hides two kinds of students.
4. **Percent correct by course and topic** (`topic_heatmap.png`, Seaborn heatmap). The weakest topic is NumPy in C102 (50%) and the strongest is Pandas (88%). In C101, functions (62%) is lower than data-structures (76%).

### 6.3 Model results
Task: tag a question with its topic (Computers, History, Mathematics, Science & Nature). Features: our TF-IDF. Split: `train_test_split(test_size=0.25, random_state=42, stratify=y)`, 388 training and 130 test questions. Both models use the same split. Results (`outputs/results/topic_model_results.json`):

| Model | Test accuracy | 5-fold CV mean ± std |
|---|---|---|
| Keyword baseline | 0.538 | – |
| Multinomial Naive Bayes | 0.769 | 0.736 ± 0.025 |
| Logistic Regression | 0.762 | 0.751 ± 0.057 |

Both models beat the baseline by more than 20 points. They are practically equal: the test difference is one question out of 130, and the cross-validation ranking is the other way round with overlapping spread. We do not claim that one is better.

The confusion matrices show the main weakness. **Mathematics** has only 60 questions, so the classifier almost never predicts it: Naive Bayes gets 0 of 15 test Mathematics questions right and Logistic Regression gets 3 of 15. Its overall accuracy is therefore mostly Computers, History and Science. The model is a suggestion tool only, and the teacher decides the topic.

## 7. Testing, error handling and ethics

### 7.1 Test cases
`python -m pytest -q` runs 377 tests, all passing. They cover empty input, a single element, duplicates, large input (for example 10,000 records and large score matrices), invalid input, a missing file, malformed JSON and the API being offline (`requests.get` is monkeypatched, so no network is used). Writing the tests found one real bug: `transform_texts([])` crashed inside scikit-learn; it now returns an empty (0-row) matrix.

### 7.2 Exception handling
All our errors derive from `LMSError`: `ValidationError`, `NotFoundError`, `DuplicateError`, `PermissionDeniedError`, `DataFileError` and `APIUnavailableError`. The menu catches `LMSError` and prints a message, so a bad choice or a missing file does not crash the program. If the API is unreachable the cache is used. A failed save keeps the previous files.

### 7.3 Ethical considerations
- **Privacy:** the repository contains fictional accounts only. Roles and enrolment limit who can see which records.
- **Bias and fairness:** the topic classifier is trained on a small, imbalanced quiz-question set, and it is weak on Mathematics. It is not used to judge any student, only to suggest a label for a question.
- **Human in control:** the teacher gives the final marks and can ignore a suggested topic. Revision tips are practice hints, not a verdict on ability.
- **Licensing and honesty:** question data is credited to Open Trivia DB (CC BY-SA 4.0), and we report the measured results, including the weak ones.

## 8. Individual contributions and conclusion

### 8.1 Contribution table

| Member | Modules and work | Commits |
|---|---|---|
| Ashbar Hussain (25k-0028) | `users.py`, `storage.py`, `assignments.py`, `admin.py`, `analysis.py`, `charts.py`; admin menu and half-release; repository layout and agreed interfaces; tests for users, storage, assignments and analysis | Parts 1, 3, 5, 6, 8, 11, 13, 15 |
| Muhammad Mudassir (25k-0153) | `exceptions.py`, `utils.py`, `courses.py`, `quizzes.py`, role menus and revision suggestions in `main.py`, `question_api.py`, `scores.py`, `text_features.py`, `topic_model.py`; tests for courses, quizzes, scores, text and API cache; design document and final README | Parts 2, 4, 7, 9, 10, 12, 14, 16, 18 |
| Both | Report (each writes the sections for their own modules), viva practice, clean-clone test | Part 17, 19 |

The commit history on GitHub matches this table: each member's commits are under their own GitHub account.

### 8.2 Challenges faced
Keeping the interfaces stable between two people (solved by agreeing all function signatures in Part 1); handling missing quiz attempts without loops (NaN mask in NumPy, NaN in Pandas); a small, uneven question set (Mathematics) that limits the classifier; and the 5-second API rate limit, which made us cache and commit the questions.

### 8.3 Conclusion and future work
ALPHA LMS runs end to end from a clean clone, covers the labs listed in Chapter 2, and has a tested, honest classifier. Future work: more Mathematics questions or class weights, a teacher-approval step for API questions, and richer charts once there are more quiz dates. Limitations: one class, local files only, small sample data.

## Appendix A — Setup and execution

Python 3.11 is recommended.

```bash
git clone https://github.com/AshbarHussain25k0028/PAI.git
cd PAI
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py               # log in as S01, T01 or A01
python -m pytest -q              # 377 tests
python src/charts.py             # regenerate the four figures
python src/topic_model.py        # regenerate the model results
```

## Appendix B — References and citations

- Open Trivia DB, https://opentdb.com (question data, CC BY-SA 4.0).
- Python standard library; NumPy, pandas, Matplotlib, seaborn, scikit-learn, requests and pytest (versions pinned in `requirements.txt`).
- Course material: AL-2001 lab manuals 01–14 and the project guidelines, Fall 2026.
- AI assistance: the project is built on the code and concepts taught in the AL-2001 labs. An AI assistant (Claude, by Anthropic) was used to improve the code, check it for errors, write and run tests, and explore libraries that were not covered in the labs.
