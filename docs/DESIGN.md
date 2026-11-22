# ALPHA LMS: design document

AL-2001 Programming for AI (Fall 2026), section BAI-3A.
Team: Ashbar Hussain (25k-0028) and Muhammad Mudassir (25k-0153).

This document explains how the program runs, which data structures and
algorithms it uses and why, how fast the main operations are, and ends with
questions we expect in the viva and exam. Function-by-function details are in
[INTERFACES.md](INTERFACES.md).

## 1. What the program is

ALPHA LMS is a Python console learning management system. Students read notes,
take quizzes, practise with online questions, submit assignments and see revision
tips. Teachers mark work and read class reports. Admins create accounts and
enroll students. All data is fictional and stored in local files.

## 2. Module map

| Module | Job | Main data structure |
|---|---|---|
| `exceptions.py` | Our own error classes under `LMSError` | class hierarchy |
| `utils.py` | Validated input loops and date helpers | none (functions) |
| `courses.py` | `Course`, `Material` | `list` of materials, `set` of enrolled IDs |
| `quizzes.py` | `Quiz`, grading, weak topics, revision tips | list of `Question` tuples, dict of topic results |
| `users.py` | `User` (abstract), `Student`, `Teacher`, `Admin` | dict of users by ID |
| `assignments.py` | `Assignment`, `Submission`, `submit_work` | dict keyed by a tuple |
| `storage.py` | JSON/CSV load and safe save, `DataStore` | dicts of ID to object |
| `admin.py` | Create accounts, enroll students | dict, set |
| `main.py` | Login and the role menu loop | dict of menu line to function |
| `question_api.py` | Open Trivia DB client with offline cache | dict cache, set of texts |
| `scores.py` | Score matrix with NumPy | 2-D array with NaN |
| `analysis.py` | Progress reports with Pandas | DataFrame |
| `charts.py` | Four labelled charts | Matplotlib figures |
| `text_features.py` | Text cleaning, TF-IDF, search | sparse matrix |
| `topic_model.py` | Question-topic classifier and comparison | trained models |

## 3. How the program runs, start to finish

1. **Start.** `python src/main.py` calls `run()`. It prints the banner.
2. **Load data.** `data_dir()` picks `data/processed/` if it contains
   `users.json`, otherwise `data/raw/`. `DataStore.load()` reads users and
   courses first (the other files refer to them), then enrollments, materials,
   quizzes, attempts, assignments and submissions. Each record is checked while
   loading, so a bad reference stops with a `DataFileError` and a clear message.
3. **Login.** `login()` asks for a user ID (for example `S01`). `find_user()`
   looks it up in the users dict in O(1). Typing `Q` quits.
4. **Menu loop.** `menu_loop()` asks the user object for `menu_options()`.
   Each role returns its own list. The chosen line is looked up in the
   `MENU_ACTIONS` dict and the matching handler runs. The loop does not check
   the role: it just calls the same methods on whatever object it got. This is
   polymorphism.
5. **Handlers.** Examples: a student takes a quiz, the answers go to
   `Quiz.grade_attempt()`, the attempt is stored in `store.attempts`, then
   `merge_topic_results()` and `suggest_revision()` produce revision tips. A
   teacher opens the class report, which builds Pandas frames and prints
   groupby tables. The topic suggestion item trains the classifier on the
   cached questions and predicts a topic for the teacher's text.
6. **Errors.** Handlers catch `LMSError` and print the message, so a wrong input
   never crashes the program. Input helpers keep asking until the value is valid.
7. **Log out and quit.** "Log out" returns to the login prompt. On `Q` (or end
   of input) the store is saved to `data/processed/` with `save_data()`. Each
   file is written to a temporary file first and then moved over the old one with
   `os.replace`, so a crash in the middle cannot leave a half-written file.
8. **Next run.** The saved copy in `data/processed/` is read instead of the
   sample data. Deleting those files restores the sample data.

The offline tools are run separately: `python src/question_api.py` refreshes
the question cache, `python src/charts.py` writes the four PNG charts to
`outputs/figures/`, and `python src/topic_model.py` trains and compares the
classifiers and writes `outputs/results/`.

## 4. Data structures and why we chose them

The course guidelines require Python's built-in `list`, `tuple`, `dict` and
`set`, so we use them directly instead of writing our own.

| Structure | Where | Why this one |
|---|---|---|
| `dict` ID to object | `DataStore.users`, `.courses`, `.quizzes`, `.assignments` | We always look records up by ID. A dict does this in O(1). A list would need a scan. |
| `set` of student IDs | `Course.enrolled` | A student cannot be enrolled twice, and "is this student enrolled?" is O(1). The set rejects duplicates for free. |
| `list` | `Course.materials`, `Quiz.questions`, `DataStore.attempts` | Order matters (notes and questions are shown in order, attempts are in time order). Append is O(1). |
| `tuple` / `namedtuple` | `Question`; submission key `(student_id, assignment_id)` | A tuple cannot be changed by accident, and it can be a dict key (lists cannot). One student has at most one submission per assignment, so the pair is a natural key. |
| `dict` of topic to `(correct, total)` | `Quiz.grade_attempt()` result | Quickly adds up results per topic across quizzes. |
| `dict` MENU_ACTIONS | `main.py` | Menu line to handler in O(1), no long if/elif chain. |
| `set` of texts | `question_api.merge_questions` | Skips questions we already have in O(1) each. |
| `set` STOP_WORDS | `text_features.py` | Fast "is this a stop word?" test. |
| NumPy 2-D array | `scores.score_matrix()` | A students-by-quizzes table. Whole-table maths with no Python loop. Missing attempts are `NaN`, not 0, so they do not drag averages down. |
| Pandas DataFrame | `analysis.py` | Labelled columns, cleaning, filtering, groupby and merge in a few lines. |
| TF-IDF sparse matrix | `text_features.py` | Most word counts are zero, so a sparse matrix saves memory. |

## 5. Object-oriented design

- **`User` is an abstract base class (ABC).** It declares `role`,
  `menu_options()` and `can_view_student()` as abstract. `Student`, `Teacher`
  and `Admin` override them. Python refuses to create a bare `User`.
- **Polymorphism.** `menu_loop()` calls `user.menu_options()` and
  `user.can_view_student(...)` without knowing the role.
- **Encapsulation.** `Submission.marks` is a property. The value is stored in
  `_marks` and the setter rejects anything below 0, above the assignment's
  maximum, or not a whole number. `User.user_id` and `User.name` are read-only
  properties.
- **Custom exceptions.** `LMSError` is the parent of `ValidationError`,
  `NotFoundError`, `DuplicateError`, `PermissionDeniedError`, `DataFileError`
  and `APIUnavailableError`. We catch specific classes only, never a bare
  `except:`.

## 6. Algorithms

### 6.1 Quiz grading by topic
`Quiz.grade_attempt(answers)` walks the questions once. It compares each answer
with `answer_index`, adds 1 to the score when right and updates the topic dict.
It returns `(score, {topic: (correct, total)})`.

### 6.2 Revision suggestions
`weak_topics()` keeps topics whose correct/total ratio is below a threshold and
sorts them with `sorted(..., key=lambda ...)`, weakest first. `suggest_revision()`
then looks up the course notes that match each weak topic. Rule-based, no model.

### 6.3 Late and open assignments
Deadlines are `datetime` objects. `is_late` is the comparison
`submitted_at > deadline`. `pending_for_student()` filters assignments the
student has not submitted and sorts them by deadline.

### 6.4 Open Trivia DB client and cache
`fetch_questions()` sends a GET request with `timeout=`, checks the HTTP status
and the API's own `response_code`. The service allows one request every five
seconds, so `_wait_for_rate_limit()` waits when needed. Replies are merged
into `data/raw/opentdb_cache.json` without duplicates. If the network is down,
`practice_set()` falls back to the cache. We committed the cache, so the app
and the classifier work with no internet.

### 6.5 NumPy score matrix (vectorised)
`score_matrix()` sorts attempts by date so the latest attempt wins, then fills
a `NaN` array with one fancy-index assignment. `to_percentages()` divides the
whole matrix by the max-score row (broadcasting) and multiplies by 100.
`quiz_averages()` and `student_averages()` compute a masked mean along axis 0 or
1. There is no Python loop over individual elements. `loop_vs_vector_demo()`
shows the vector version is about 8 times faster than a loop.

### 6.6 Pandas progress report
Records become DataFrames. `clean_frame()` drops duplicates, trims and
upper-cases IDs, parses dates and turns blank marks into `NaN`.
`course_summary()` and `topic_summary()` use `groupby`. `class_report()` filters
one course, aggregates per student and merges quiz and assignment results
(outer merge so a student with no quiz still appears). `needs_attention()`
filters students below the pass mark or with missing work.

### 6.7 Text cleaning and TF-IDF
`clean_text()` unescapes HTML, lowercases, keeps letters only and removes stop
words. TF-IDF scores a word high when it is frequent in one question and rare
across all questions, so "photosynthesis" counts and "the" does not. The
vectoriser is **fitted on the training texts only**, then applied to the test
texts, so nothing from the test set leaks into training. `search()` ranks stored
questions by cosine similarity with the query.

### 6.8 Topic classifier
Open Trivia DB questions are labelled by category (Computers, History,
Mathematics, Science & Nature). We split them 75 / 25 with
`train_test_split(test_size=0.25, random_state=42, stratify=y)`. We compare
three methods on the same split:

| Method | Test accuracy | 5-fold CV mean (std) |
|---|---|---|
| Keyword baseline | 0.538 | not applicable |
| Multinomial Naive Bayes | 0.769 | 0.736 (0.025) |
| Logistic Regression | 0.762 | 0.751 (0.057) |

Naive Bayes counts which words usually appear in each topic. Logistic
Regression learns a weight per word. Both clearly beat the keyword baseline. The
two models are close, and cross-validation (which tests on five different
splits) shows Logistic Regression slightly ahead on average, so the single-split
winner is not a safe claim. Mathematics is the weakest class: the API has only
60 multiple-choice maths questions, and Naive Bayes got none of them right on
the test split. The classifier only **suggests** a topic. The teacher decides.

## 7. Time and space complexity of the main operations

Notation: u users, c courses, m materials, q questions, a attempts,
s students, z quizzes, n rows, v vocabulary size.

| Operation | Time | Space | Notes |
|---|---|---|---|
| Find a user, course, quiz or assignment by ID | O(1) | O(1) | dict lookup |
| Enroll a student / check enrollment | O(1) | O(1) | set add / `in` |
| Add a material | O(m) | O(1) | duplicate check scans the list |
| Add a question to a quiz | O(q) | O(1) | duplicate check |
| Grade one attempt | O(q) | O(t) for t topics | one pass |
| `weak_topics` | O(t log t) | O(t) | sort |
| `suggest_revision` | O(t log t + t·m) | O(t·m) | sort, then notes lookup |
| Pending assignments for a student | O(a log a) | O(a) | filter + sort by deadline |
| Login / menu choice | O(1) | O(1) | dict lookup |
| Load all data | O(N) | O(N) | N records in all files |
| Safe save | O(N) | O(N) | temp file then replace |
| `score_matrix` | O(a log a + s·z) | O(s·z) | sort, then one assignment |
| Percentages, mask, averages | O(s·z) | O(s·z) | vectorised, no element loop |
| Pandas groupby / clean | O(n) | O(n) | hash grouping |
| `class_report` | O(n log n) | O(n) | merge and sort |
| `clean_text` | O(k) for k characters | O(k) | |
| TF-IDF fit | O(N) for N words | O(N) sparse | |
| `search` | O(n·v) | O(n) | cosine similarity over n texts |
| Train Naive Bayes / Logistic Regression | about O(n·v) per pass | O(v · classes) | Logistic Regression repeats passes until it converges |
| Cross-validation | folds × training cost | same as one fit | 5 folds |
| API fetch (cache miss) | one network call, then O(q) | O(q) | 5 s rate limit between calls |

## 8. Error handling and safety

- Only specific `except` blocks. Every file is opened with `with`. Every
  `requests` call has `timeout=`.
- Safe save: write a temporary file, then `os.replace`. If writing fails, the
  old file is kept.
- Input is validated at the edge: IDs, menu numbers, dates, marks range.
- No passwords, API keys or real student data. The login only needs a fictional
  user ID, which is acceptable for a classroom demo but is **not** real
  authentication (see limitations in the README).

## 9. Testing

`python -m pytest -q` runs 377 tests. They cover empty input, a single element,
duplicates, large input (10,000 records, a 1000 × 50 matrix), invalid input,
missing files, malformed JSON and the API being offline (`requests.get` is
replaced by a function that fails, so tests need no internet). Writing the
tests found one real bug: `transform_texts([])` crashed inside scikit-learn. It
now returns an empty matrix.

## 10. Likely viva and exam questions

**Program and design**

1. *Walk us through what happens when a student logs in and takes a quiz.*
   `run()` loads the store, `login()` finds the user in the users dict,
   `menu_loop()` shows `Student.menu_options()`, the choice is looked up in
   `MENU_ACTIONS` and `take_quiz()` runs. Answers go to `Quiz.grade_attempt()`,
   the attempt is appended to `store.attempts`, and on exit everything is saved.
2. *Why a console program and not a web app?* The course scope and the proposal
   say console only. It keeps the focus on data structures, files, NumPy, Pandas
   and the model.
3. *What is polymorphism here?* The menu loop calls `menu_options()` and
   `can_view_student()` on a `User`. Each subclass answers in its own way.
4. *What is an abstract base class and why use one?* A class that cannot be
   created directly. `User` forces every role to implement the methods the menu
   needs, so a new role cannot be forgotten half-finished.
5. *Why a property for marks?* So the only way to change a mark goes through the
   setter, which rejects values outside 0 to the maximum. That is encapsulation.
6. *Why custom exceptions?* They let us catch exactly our own errors
   (`except LMSError`) and print a friendly message, without hiding real bugs
   the way a bare `except:` would.
7. *Why write to a temp file then replace?* If the program dies in the middle of
   a write, the old file is still intact. `os.replace` swaps the file in one step.

**Data structures**

8. *Why a set for enrolled students?* No duplicates, and O(1) membership checks.
9. *Why can a tuple be a dict key but not a list?* A tuple is immutable and so
   hashable. A list can change, so it has no stable hash.
10. *Why dict for users instead of a list?* Lookup by ID is O(1) instead of O(n).
11. *Difference between list, tuple, set and dict?* List: ordered and
    changeable. Tuple: ordered and fixed. Set: unordered, unique values. Dict:
    key to value pairs with O(1) average lookup.
12. *What is the complexity of `x in some_list` versus `x in some_set`?* O(n)
    versus O(1) on average.
13. *What does `sorted(key=lambda ...)` do in your code?* It sorts topics by
    their correct ratio so the weakest comes first.

**NumPy and Pandas**

14. *What is broadcasting?* NumPy stretches a smaller array to the shape of a
    bigger one so `matrix / max_scores * 100` works in one line.
15. *Why NaN and not 0 for a missed quiz?* Zero would say the student scored
    nothing and lower their average. NaN means "no data" and `nanmean` ignores it.
16. *What does `axis=0` mean?* Collapse the rows, giving one value per column
    (per quiz). `axis=1` gives one value per row (per student).
17. *Why is vectorised code faster than a loop?* The loop runs in the Python
    interpreter one element at a time. NumPy runs compiled C over the whole
    array. Our demo measured about 8 times faster.
18. *What does groupby do?* It splits rows into groups by a key, applies an
    aggregate such as mean to each group, and combines the results.
19. *Inner versus outer merge?* Inner keeps only keys present on both sides.
    Outer keeps all keys, filling gaps with NaN. We use outer so a student who
    skipped every quiz still shows in the class report.

**API and files**

20. *Why `timeout=` in `requests.get`?* Without it a dead server can hang the
    program forever.
21. *Why check both the HTTP status and `response_code`?* Open Trivia DB can
    reply with HTTP 200 but a response code that means "not enough questions"
    or "rate limited".
22. *Why a cache?* Faster, works offline, respects the 5-second rate limit, and
    gives the classifier a fixed dataset so results can be repeated.
23. *Why `with open(...)`?* The file is closed automatically, even if an error
    occurs.

**Machine learning**

24. *What is a train/test split and why `random_state=42`?* We hide 25% of the
    data to test on unseen examples. The seed makes the split repeatable.
25. *What is `stratify=y`?* Each category keeps about the same share in the
    training and test sets.
26. *What is TF-IDF?* Term frequency times inverse document frequency. Words
    common in one text but rare overall get high weights.
27. *Why fit TF-IDF on the training data only?* Fitting on all data would let
    test-set information leak into training and make accuracy look better than
    it is (data leakage).
28. *How do Naive Bayes and Logistic Regression differ?* Naive Bayes uses word
    counts per class and assumes words are independent. Logistic Regression
    learns a weight for each word and fits a linear boundary.
29. *Which model won?* On the single test split Naive Bayes (0.769 versus 0.762).
    In 5-fold cross-validation Logistic Regression is a little higher (0.751
    versus 0.736) but less stable (std 0.057 versus 0.025). The two are close, so
    we do not claim one is clearly better.
30. *What is cross-validation?* We split the data into 5 folds, train on 4 and
    test on 1, rotate, and average. It gives a steadier estimate than one split.
31. *What is the keyword baseline for?* To show the models learn something. A
    model that cannot beat counting keywords is not useful (ours reach 0.76 to
    0.77 versus 0.54).
32. *Why does Mathematics score badly?* Only 60 maths questions exist, so the
    training set is small and imbalanced. Naive Bayes missed all of them on the
    test split.
33. *Is accuracy enough?* No. The confusion matrix and per-class precision and
    recall show where it fails, such as Mathematics.
34. *Can the model grade students?* No. It only suggests a topic for a question
    and the teacher decides. Grading stays with the teacher.

**Ethics and limits**

35. *What are the privacy and bias risks?* Real grades and identities must not be
    committed, so all data is fictional. The classifier comes from trivia
    questions, so it may not suit questions from a real course. Revision tips
    are advice, not a judgement of ability.
36. *What are the main limitations?* No real passwords, local files instead of a
    database, one user at a time, a small sample data set and a classifier that
    is weak on Mathematics.
