# Agreed module interfaces

Agreed in Part 1. Every function below exists in `src/` with this name and these
parameters; its body is filled in by the part shown. Later parts may add small
helper functions but must not change these signatures.

Run the program with `python src/main.py` from the repo root. Modules import each
other by plain name (for example `from users import Student`).

## `exceptions.py` (owner: Muhammad Mudassir, Part 2)

| Class | Parent | Used when | Owner | Part |
|---|---|---|---|---|
| `LMSError` | `Exception` | Base class for every error raised on purpose by ALPHA LMS. | Muhammad Mudassir | 2 |
| `ValidationError` | `LMSError` | A value typed by the user, or read from a file, is not valid. | Muhammad Mudassir | 2 |
| `NotFoundError` | `LMSError` | An ID (user, course, quiz, assignment ...) does not exist. | Muhammad Mudassir | 2 |
| `DuplicateError` | `LMSError` | Something with the same ID or key already exists. | Muhammad Mudassir | 2 |
| `PermissionDeniedError` | `LMSError` | The logged-in user is not allowed to do this action. | Muhammad Mudassir | 2 |
| `DataFileError` | `LMSError` | A data file is missing, unreadable or badly formatted. | Muhammad Mudassir | 2 |
| `APIUnavailableError` | `LMSError` | The online question API could not be reached or sent a bad reply. | Muhammad Mudassir | 2 |

## `utils.py` (owner: Muhammad Mudassir, Part 2)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `ask_int` | prompt, low, high | the number the user typed, as an int. | O(1) per attempt | Muhammad Mudassir | 2 |
| `ask_choice` | title, options | an int from 1 to len(options). | O(n) to print n options | Muhammad Mudassir | 2 |
| `ask_text` | prompt, allow_empty | the cleaned text. | O(k) for k characters | Muhammad Mudassir | 2 |
| `parse_datetime` | text | datetime.datetime | O(1) | Muhammad Mudassir | 2 |
| `format_datetime` | moment | the date as text in DATE_FORMAT. | O(1) | Muhammad Mudassir | 2 |
| `make_id` | prefix, existing_ids | a new ID that is not in existing_ids. | O(n) for n existing IDs | Muhammad Mudassir | 2 |
| `require_text` (helper) | value, field | the value stripped; ValidationError if missing or empty. | O(k) for k characters | Muhammad Mudassir | 2 |

## `courses.py` (owner: Muhammad Mudassir, Part 2)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `Material.__init__` | material_id, course_id, title, topic, file_name | a new object | O(1) | Muhammad Mudassir | 2 |
| `Material.to_dict` | – | dict with the keys of materials.csv. | O(1) | Muhammad Mudassir | 2 |
| `Material.from_dict` | row | a new Material. | O(1) | Muhammad Mudassir | 2 |
| `Course.__init__` | course_id, title, teacher_id | a new object | O(1) | Muhammad Mudassir | 2 |
| `Course.enroll` | student_id | True if added, False if they were already enrolled. | O(1) because of the set | Muhammad Mudassir | 2 |
| `Course.unenroll` | student_id | None | O(1) | Muhammad Mudassir | 2 |
| `Course.is_enrolled` | student_id | True if enrolled. | O(1) because of the set | Muhammad Mudassir | 2 |
| `Course.add_material` | material | None | O(m) for m materials (the duplicate check) | Muhammad Mudassir | 2 |
| `Course.materials_for_topic` | topic | list of matching Material objects, in display order. | O(m) for m materials | Muhammad Mudassir | 2 |
| `Course.to_dict` | – | {"course_id", "title", "teacher_id"}. | O(1) | Muhammad Mudassir | 2 |
| `Course.from_dict` | row | a new Course (no materials or students yet). | O(1) | Muhammad Mudassir | 2 |

## `users.py` (owner: Ashbar Hussain, Part 3)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `User.__init__` | user_id, name | a new object | O(1) | Ashbar Hussain | 3 |
| `User.user_id`, `User.name` (read-only properties) | – | the stored ID / name (added in Part 3) | O(1) | Ashbar Hussain | 3 |
| `User.role (property)` | – | "student", "teacher" or "admin". | O(1) | Ashbar Hussain | 3 |
| `User.menu_options` | – | list of menu lines, in display order. | O(1) | Ashbar Hussain | 3 |
| `User.can_view_student` | student_id, courses | True if allowed. | Student/Admin O(1); Teacher O(c) for c courses | Ashbar Hussain | 3 |
| `User.describe` | – | text such as "S01 - Ali Raza (student)". | O(1) | Ashbar Hussain | 3 |
| `User.to_dict` | – | {"user_id", "name", "role"}. | O(1) | Ashbar Hussain | 3 |
| `Student.role (property)` | – | "student". | O(1) | Ashbar Hussain | 3 |
| `Student.menu_options` | – | list of menu lines (my courses, quizzes, assignments, progress). | O(1) | Ashbar Hussain | 3 |
| `Student.can_view_student` | student_id, courses | True only if student_id is their own ID. | O(1) | Ashbar Hussain | 3 |
| `Teacher.role (property)` | – | "teacher". | O(1) | Ashbar Hussain | 3 |
| `Teacher.menu_options` | – | list of menu lines (materials, quizzes, marking, class report). | O(1) | Ashbar Hussain | 3 |
| `Teacher.can_view_student` | student_id, courses | True if the student is in one of this teacher's courses. | O(c) for c courses (set lookup inside each course) | Ashbar Hussain | 3 |
| `Admin.role (property)` | – | "admin". | O(1) | Ashbar Hussain | 3 |
| `Admin.menu_options` | – | list of menu lines (accounts, enrollment, save). | O(1) | Ashbar Hussain | 3 |
| `Admin.can_view_student` | student_id, courses | always True. | O(1) | Ashbar Hussain | 3 |
| `user_from_dict` | record | a Student, Teacher or Admin object. | O(1) | Ashbar Hussain | 3 |
| `find_user` | users, user_id | the matching User. | O(1) | Ashbar Hussain | 3 |

## `quizzes.py` (owner: Muhammad Mudassir, Part 4 / 7)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `Quiz.__init__` | quiz_id, course_id, title | a new object | O(1) | Muhammad Mudassir | 4 |
| `Quiz.add_question` | question | None | O(n) for n questions (the duplicate check) | Muhammad Mudassir | 4 |
| `Quiz.max_score (property)` | – | the number of questions (1 mark each). | O(1) | Muhammad Mudassir | 4 |
| `Quiz.grade_attempt` | answers | (score, topic_results) where topic_results is {topic: (correct, total)}. | O(n) for n questions | Muhammad Mudassir | 4 |
| `Quiz.to_dict` | – | dict in the same shape as one record of quizzes.json. | O(n) for n questions | Muhammad Mudassir | 4 |
| `Quiz.from_dict` | record | a new Quiz with its questions. | O(n^2) worst case for n questions (duplicate check per add; n is small) | Muhammad Mudassir | 4 |
| `weak_topics` | topic_results, threshold | list of topic names, lowest ratio first. | O(t log t) for t topics | Muhammad Mudassir | 7 |
| `suggest_revision` | topic_results, course, threshold | [(topic, [Material, ...]), ...], weakest topic first. | O(t log t + t*m) for t topics and m materials | Muhammad Mudassir | 7 |

## `storage.py` (owner: Ashbar Hussain, Part 5)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `load_json` | path | the parsed list or dict. | O(n) for n characters | Ashbar Hussain | 5 |
| `save_json` | path, data | None | O(n) for n characters written | Ashbar Hussain | 5 |
| `load_csv` | path | list of dicts, one per row (values are strings). | O(r) for r rows | Ashbar Hussain | 5 |
| `save_csv` | path, rows, fieldnames | None | O(r) for r rows | Ashbar Hussain | 5 |
| `data_dir` | – | PROCESSED_DIR if it has users.json, otherwise RAW_DIR. | O(1) | Ashbar Hussain | 5 |
| `DataStore.__init__` | – | a new object | O(1) | Ashbar Hussain | 5 |
| `DataStore.load` | folder | None | O(N) for N records in all files | Ashbar Hussain | 5 |
| `DataStore.save` | folder | None | O(N) for N records | Ashbar Hussain | 5 |
| `DataStore.courses_for_student` | student_id | list of Course objects. | O(c) for c courses (set lookup in each) | Ashbar Hussain | 5 |
| `DataStore.courses_for_teacher` | teacher_id | list of Course objects. | O(c) for c courses | Ashbar Hussain | 5 |

## `assignments.py` (owner: Ashbar Hussain, Part 6)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `Assignment.__init__` | assignment_id, course_id, title, deadline, max_marks | a new object | O(1) | Ashbar Hussain | 6 |
| `Assignment.is_open` | now | True if now <= deadline. | O(1) | Ashbar Hussain | 6 |
| `Assignment.to_dict` | – | dict with the keys of assignments.json (deadline as text). | O(1) | Ashbar Hussain | 6 |
| `Assignment.from_dict` | record | a new Assignment. | O(1) | Ashbar Hussain | 6 |
| `Submission.__init__` | student_id, assignment_id, submitted_at, text, max_marks | a new object | O(1) | Ashbar Hussain | 6 |
| `Submission.key (property)` | – | (student_id, assignment_id). | O(1) | Ashbar Hussain | 6 |
| `Submission.marks (property)` | – | int, or None if not marked yet. | O(1) | Ashbar Hussain | 6 |
| `Submission.marks (setter)` | value | None | O(1) | Ashbar Hussain | 6 |
| `Submission.is_late` | assignment | True if submitted_at > assignment.deadline. | O(1) | Ashbar Hussain | 6 |
| `Submission.to_dict` | – | dict with the columns of submissions.csv (blank marks if None). | O(1) | Ashbar Hussain | 6 |
| `Submission.from_dict` | row, max_marks | a new Submission (marked if the marks column is not blank). | O(1) | Ashbar Hussain | 6 |
| `submit_work` | submissions, assignment, student_id, text, now | the new Submission (late ones are accepted and flagged by is_late). | O(1) | Ashbar Hussain | 6 |
| `pending_for_student` | assignments, submissions, student_id, course_ids | list of Assignment, earliest deadline first. | O(a log a) for a assignments | Ashbar Hussain | 6 |

## `main.py` (owner: Muhammad Mudassir / Ashbar Hussain, Part 1, 7, 8)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `show_banner` | – | None | O(1) | Ashbar Hussain | 1 |
| `run` | – | None | O(1) | Ashbar Hussain (Part 1), Muhammad Mudassir (Part 7) | 1, 7 |

## `question_api.py` (owner: Muhammad Mudassir, Part 9)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `fetch_questions` | category_id, amount | list of question dicts as sent by the API. | O(q) for q questions in the reply | Muhammad Mudassir | 9 |
| `load_cache` | path | {category_name: [question dicts]}; empty dict if no cache yet. | O(q) for q cached questions | Muhammad Mudassir | 9 |
| `save_cache` | cache, path | None | O(q) for q questions | Muhammad Mudassir | 9 |
| `build_cache` | per_category | the updated cache dict. | O(k * q) for k categories and q questions each | Muhammad Mudassir | 9 |
| `to_quiz_question` | api_question, question_id, topic | quizzes.Question with 4 shuffled options and the right answer_index. | O(1) | Muhammad Mudassir | 9 |

## `scores.py` (owner: Muhammad Mudassir, Part 10)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `score_matrix` | attempts, student_ids, quiz_ids | numpy array of shape (len(student_ids), len(quiz_ids)); NaN where a student has no attempt (the latest attempt wins if there are two). | O(a + s*q) for a attempts, s students, q quizzes | Muhammad Mudassir | 10 |
| `to_percentages` | matrix, max_scores | (s, q) array: matrix / max_scores * 100 (NaN stays NaN). | O(s*q), vectorised | Muhammad Mudassir | 10 |
| `missing_mask` | matrix | boolean (s, q) array, True where the value is NaN. | O(s*q), vectorised | Muhammad Mudassir | 10 |
| `quiz_averages` | matrix | length-q array (np.nanmean along axis=0). | O(s*q), vectorised | Muhammad Mudassir | 10 |
| `student_averages` | matrix | length-s array (np.nanmean along axis=1). | O(s*q), vectorised | Muhammad Mudassir | 10 |
| `loop_vs_vector_demo` | size | (loop_seconds, vector_seconds). | O(size) | Muhammad Mudassir | 10 |

## `analysis.py` (owner: Ashbar Hussain, Part 11)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `build_progress_frame` | attempts, quizzes | DataFrame with student_id, quiz_id, course_id, attempted_on, score, max_score, percent. | O(a) for a attempts | Ashbar Hussain | 11 |
| `build_submission_frame` | submissions, assignments | DataFrame with student_id, assignment_id, course_id, submitted_at, marks, max_marks, percent, late. | O(n) for n submissions | Ashbar Hussain | 11 |
| `clean_frame` | frame | a new, cleaned DataFrame. | O(n) for n rows | Ashbar Hussain | 11 |
| `course_summary` | progress | DataFrame indexed by course_id with mean_percent and attempts. | O(n) for n rows | Ashbar Hussain | 11 |
| `topic_summary` | attempts, quizzes | DataFrame with course_id, topic, correct, total, percent. | O(a * k) for a attempts of k questions | Ashbar Hussain | 11 |
| `class_report` | progress, submissions, course_id | DataFrame with student_id, quiz_avg, assignment_avg, missing_work. | O(n) for n rows (merge on student_id) | Ashbar Hussain | 11 |

## `text_features.py` (owner: Muhammad Mudassir, Part 12)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `clean_text` | text | lowercase words without punctuation, digits or stop-words, joined by single spaces. | O(k) for k characters | Muhammad Mudassir | 12 |
| `tokenize` | text | list of words from clean_text(text). | O(k) for k characters | Muhammad Mudassir | 12 |
| `fit_vectorizer` | train_texts | (vectorizer, X_train) where X_train is a sparse matrix. | O(N) for N words in all training texts | Muhammad Mudassir | 12 |
| `transform_texts` | vectorizer, texts | sparse matrix with one row per text. | O(N) for N words | Muhammad Mudassir | 12 |
| `search` | query, texts, top_k | [(index, score), ...], best match first. | O(n * v) for n texts and v vocabulary size | Muhammad Mudassir | 12 |

## `charts.py` (owner: Ashbar Hussain, Part 13)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `quiz_average_line` | progress, path | the Path of the saved PNG. | O(n) for n rows | Ashbar Hussain | 13 |
| `completion_bar` | submissions, students_per_course, path | the Path of the saved PNG. | O(n) for n rows | Ashbar Hussain | 13 |
| `score_histogram` | percentages, path | the Path of the saved PNG. | O(n) for n values | Ashbar Hussain | 13 |
| `topic_heatmap` | topic_table, path | the Path of the saved PNG. | O(c*t) for c courses and t topics | Ashbar Hussain | 13 |

## `topic_model.py` (owner: Muhammad Mudassir, Part 14)

| Function | Inputs | Output | Big-O | Owner | Part |
|---|---|---|---|---|---|
| `load_dataset` | cache | (texts, labels), two lists of the same length. | O(q) for q questions | Muhammad Mudassir | 14 |
| `split_data` | texts, labels | (X_train, X_test, y_train, y_test). | O(q) | Muhammad Mudassir | 14 |
| `keyword_baseline` | texts, keywords | predicted category for each text (most hits wins). | O(q * w) for q texts of w words | Muhammad Mudassir | 14 |
| `train_models` | X_train, y_train | {"naive_bayes": model, "logistic_regression": model}. | depends on the model; about O(n * v) for n rows, v words | Muhammad Mudassir | 14 |
| `evaluate` | model, X_test, y_test | {"accuracy": float, "report": str, "confusion": list of lists}. | O(n * v) | Muhammad Mudassir | 14 |
| `cross_validate` | texts, labels, folds | {model_name: (mean_accuracy, std_accuracy)}. | O(folds * training cost) | Muhammad Mudassir | 14 |
| `save_results` | results, folder | the Path of the saved metrics file. | O(1) for a fixed number of models | Muhammad Mudassir | 14 |
| `suggest_topic` | model, vectorizer, question_text | the predicted category name (the teacher can change it). | O(w) for w words | Muhammad Mudassir | 14 |


## Main data structures

| Structure | Where | Why this one | Key operations |
|---|---|---|---|
| `dict` id → object | `DataStore.users`, `.courses`, `.assignments`, `.quizzes` | Find a record by ID instantly | get/add: O(1) |
| `set` of student IDs | `Course.enrolled` | No duplicate enrollments, fast "is enrolled?" check | add/check/remove: O(1) |
| `list` | `Course.materials`, `Quiz.questions`, `DataStore.attempts` | Keeps display order | append O(1), show all O(n) |
| `tuple` | `Question`, submission key `(student_id, assignment_id)` | Fixed record that can't be changed by accident, usable as a dict key | O(1) |
| NumPy 2-D array | `scores.score_matrix()` | Fast maths on a whole table at once | mean along an axis: O(s·q) |
| Pandas DataFrame | `analysis.build_progress_frame()` | Labelled table for cleaning and groupby | groupby: O(n) |

## Data files

The app reads from `data/processed/` if `users.json` exists there, otherwise from
`data/raw/`, and always saves to `data/processed/`. All sample data is fictional.

| File | Columns / fields |
|---|---|
| `users.json` | user_id, name, role (A01 admin, T01-T02 teachers, S01-S08 students) |
| `courses.csv` | course_id, title, teacher_id |
| `enrollments.csv` | student_id, course_id |
| `materials.csv` | material_id, course_id, title, topic, file_name (notes in `data/raw/notes/`) |
| `quizzes.json` | quiz_id, course_id, title, questions [question_id, text, options (4), answer_index, topic] |
| `attempts.json` | attempt_id, student_id, quiz_id, attempted_on, answers, score, max_score |
| `assignments.json` | assignment_id, course_id, title, deadline ("YYYY-MM-DD HH:MM"), max_marks |
| `submissions.csv` | student_id, assignment_id, submitted_at, text, marks (blank = not marked), feedback |

Topics: C101 → data-structures, functions, oop, files; C102 → numpy, pandas, charts.
