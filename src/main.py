"""ALPHA LMS console entry point. Run from the repo root:

    python src/main.py

Owner: Muhammad Mudassir (Part 7: login and role menus),
       Ashbar Hussain (Part 1: this starting version, Part 8: admin menu).

How the menus work (Part 7)
---------------------------
After login, every role goes through the same loop: the loop asks the user
object for user.menu_options() and runs the handler for the chosen line. It
never checks "is this a student?", because Student, Teacher and Admin each
return their own menu lines. This is polymorphism.

Key data structure: MENU_ACTIONS is a dict {menu line: handler function}, so
finding what to run for a choice is O(1).

Student and teacher flows cover courses, materials and quizzes (Part 7).
Part 8 adds the assignment items (students submit, teachers mark), the admin
menu (list and create accounts, enroll students, save) and saving on exit:
every change made in a session is written to data/processed/ when the
program ends. The class report comes in Part 11.
Part 9 adds "Practice questions" for students: extra multiple-choice
questions from Open Trivia DB, or from the saved cache when offline.
"""

from __future__ import annotations

from datetime import datetime

from admin import accounts_by_role, create_account, enroll_student, students_not_in
from assignments import submit_work
from exceptions import DataFileError, LMSError
from question_api import CATEGORIES, practice_set
from quizzes import Quiz, merge_topic_results, suggest_revision, weak_topics
from storage import PROCESSED_DIR, RAW_DIR, DataStore
from users import find_user
from utils import ask_choice, ask_int, ask_text, format_datetime, make_id

BANNER = "ALPHA LMS - Learning Management System"
NOTES_DIR = RAW_DIR / "notes"      # teacher notes, one .txt per material
LOG_OUT = "Log out"
PRACTICE_COUNT = 5                 # questions per practice round (Part 9)


def show_banner() -> None:
    """Print the program title between two lines.

    Complexity: O(1).
    """
    line = "=" * len(BANNER)
    print(line)
    print(BANNER)
    print(line)


# ---------------------------------------------------------------- helpers

def courses_for(store: DataStore, user) -> list:
    """Courses the user works with: enrolled (student) or taught (teacher).

    Args:
        store: the loaded DataStore.
        user: the logged-in User.
    Returns:
        list of Course objects (every course for an admin).
    Complexity: O(c) for c courses.
    """
    if user.role == "student":
        return store.courses_for_student(user.user_id)
    if user.role == "teacher":
        return store.courses_for_teacher(user.user_id)
    return list(store.courses.values())


def choose_from(title: str, items: list, label):
    """Let the user pick one item from a list, or go back.

    Args:
        title: heading of the menu.
        items: the objects to choose from.
        label: function that turns an item into its menu line.
    Returns:
        the chosen item, or None if the list is empty or "Back" was chosen.
    Complexity: O(n) for n items.
    """
    if not items:
        print("Nothing to show here yet.")
        return None
    choice = ask_choice(title, [label(item) for item in items] + ["Back"])
    return None if choice == len(items) + 1 else items[choice - 1]


def read_note(file_name: str) -> str:
    """Read one teacher note from data/raw/notes.

    Args:
        file_name: e.g. "c101_oop.txt".
    Returns:
        the text of the note.
    Raises:
        DataFileError: if the file is missing or cannot be read.
    Complexity: O(k) for k characters.
    """
    try:
        with open(NOTES_DIR / file_name, encoding="utf-8") as file:
            return file.read().strip()
    except OSError as error:
        raise DataFileError(f"Could not read the note {file_name}.") from error


def latest_attempts(store: DataStore, student_id: str) -> dict:
    """The newest attempt of a student for each quiz.

    Attempts are stored oldest first, so a later one overwrites an older one.

    Args:
        store: the loaded DataStore.
        student_id: e.g. "S01".
    Returns:
        dict {quiz_id: attempt record}.
    Complexity: O(a) for a attempts.
    """
    latest = {}   # quiz_id -> attempt dict
    for attempt in store.attempts:
        if attempt["student_id"] == student_id:
            latest[attempt["quiz_id"]] = attempt
    return latest


def topic_results_for(store: DataStore, student_id: str, course_id: str) -> dict:
    """Re-grade a student's latest attempts in one course, merged by topic.

    Args:
        store: the loaded DataStore.
        student_id: the student.
        course_id: only quizzes of this course count.
    Returns:
        dict {topic: (correct, total)} over all their latest attempts.
    Complexity: O(a + q * n) for a attempts and q quizzes of n questions.
    """
    results = []
    for quiz_id, attempt in latest_attempts(store, student_id).items():
        quiz = store.quizzes[quiz_id]
        if quiz.course_id == course_id:
            results.append(quiz.grade_attempt(attempt["answers"])[1])
    return merge_topic_results(results)


def print_suggestions(suggestions: list) -> None:
    """Show revision tips: each weak topic and the notes to read.

    Args:
        suggestions: [(topic, [Material, ...]), ...] from suggest_revision().
    Complexity: O(t * m) for t topics and m materials each.
    """
    if not suggestions:
        print("  No weak topics, well done!")
        return
    for rank, (topic, materials) in enumerate(suggestions, start=1):
        titles = ", ".join(f"{m.title} ({m.file_name})" for m in materials)
        print(f"  {rank}. {topic}: revise {titles or 'ask your teacher for notes'}")


def print_topic_table(topic_results: dict) -> None:
    """Print correct/total and percentage for each topic.

    Args:
        topic_results: {topic: (correct, total)}.
    Complexity: O(t log t) for t topics (sorted by name).
    """
    for topic, (correct, total) in sorted(topic_results.items()):
        percent = correct / total * 100 if total else 0
        print(f"  {topic:<16} {correct}/{total}  ({percent:.0f}%)")


# ---------------------------------------------------------------- handlers

def show_courses(store: DataStore, user) -> None:
    """List the user's courses; open one to see and read its materials.

    Args:
        store: the loaded DataStore.
        user: the logged-in User (student or teacher).
    Complexity: O(c + m) for c courses and m materials.
    """
    course = choose_from("Your courses", courses_for(store, user),
                         lambda c: f"{c.course_id} {c.title} ({len(c.enrolled)} students)")
    if course is None:
        return
    material = choose_from(f"Materials for {course.course_id}", course.materials,
                           lambda m: f"{m.title} [topic: {m.topic}]")
    if material is not None:
        print(f"\n--- {material.title} ---")
        print(read_note(material.file_name))


def ask_answers(quiz) -> list[int]:
    """Ask every question of a quiz and collect the chosen options.

    Args:
        quiz: the Quiz being taken.
    Returns:
        list of option indexes (0-3), one per question, in order.
    Complexity: O(n) for n questions.
    """
    answers = []
    for number, question in enumerate(quiz.questions, start=1):
        print(f"\nQuestion {number} of {quiz.max_score}")
        choice = ask_choice(question.text, list(question.options))
        answers.append(choice - 1)        # the menu starts at 1, indexes at 0
    return answers


def record_attempt(store: DataStore, student_id: str, quiz, answers: list) -> int:
    """Grade the answers and add the attempt to store.attempts.

    Args:
        store: the loaded DataStore.
        student_id: who took the quiz.
        quiz: the Quiz.
        answers: option indexes from ask_answers().
    Returns:
        the score.
    Complexity: O(n + a) for n questions and a attempts (new ID).
    """
    score, _ = quiz.grade_attempt(answers)
    attempt_ids = {attempt["attempt_id"] for attempt in store.attempts}
    store.attempts.append({
        "attempt_id": make_id("AT", attempt_ids), "student_id": student_id,
        "quiz_id": quiz.quiz_id, "attempted_on": format_datetime(datetime.now()),
        "answers": answers, "score": score, "max_score": quiz.max_score})
    return score


def take_quiz(store: DataStore, user) -> None:
    """Student flow: choose a quiz from your courses, answer it, see tips.

    Args:
        store: the loaded DataStore.
        user: the logged-in Student.
    Complexity: O(q + n) for q quizzes and n questions.
    """
    course_ids = {course.course_id for course in courses_for(store, user)}
    quizzes = [quiz for quiz in store.quizzes.values()
               if quiz.course_id in course_ids]
    quiz = choose_from("Choose a quiz", quizzes,
                       lambda q: f"{q.quiz_id} {q.title} ({q.max_score} questions)")
    if quiz is None:
        return
    answers = ask_answers(quiz)
    score = record_attempt(store, user.user_id, quiz, answers)
    print(f"\nYou scored {score}/{quiz.max_score}.")
    topic_results = quiz.grade_attempt(answers)[1]
    print_topic_table(topic_results)
    print("Revision tips:")
    print_suggestions(suggest_revision(topic_results, store.courses[quiz.course_id]))


def practice_questions(store: DataStore, user) -> None:
    """Student flow: answer practice questions from Open Trivia DB.

    Questions come live from the API, or from the saved cache when there is
    no internet (Part 9). Practice scores are shown but not saved, because
    they are not part of any course quiz.

    Args:
        store: the loaded DataStore (not needed; same call as other handlers).
        user: the logged-in Student.
    Complexity: O(q) for q cached questions in the chosen category.
    """
    names = list(CATEGORIES)
    category = names[ask_choice("Practice category", names) - 1]
    questions, source = practice_set(category, PRACTICE_COUNT)
    print(f"\n{len(questions)} {category} questions ({source}).")
    quiz = Quiz("PRACTICE", "OPENTDB", f"{category} practice")
    for question in questions:
        quiz.add_question(question)
    answers = ask_answers(quiz)
    score = quiz.grade_attempt(answers)[0]
    print(f"\nPractice score: {score}/{quiz.max_score}.")
    for question, answer in zip(quiz.questions, answers):
        if answer != question.answer_index:
            print(f"- {question.text}\n  Answer: {question.options[question.answer_index]}")


def show_progress(store: DataStore, user) -> None:
    """Student flow: topic scores and revision tips for each course.

    Args:
        store: the loaded DataStore.
        user: the logged-in Student.
    Complexity: O(c * (a + q * n)) for c courses.
    """
    for course in courses_for(store, user):
        topic_results = topic_results_for(store, user.user_id, course.course_id)
        print(f"\n{course.course_id} {course.title}")
        if not topic_results:
            print("  No quiz attempts yet.")
            continue
        print_topic_table(topic_results)
        print("Revision tips:")
        print_suggestions(suggest_revision(topic_results, course))


def show_quiz_results(store: DataStore, user) -> None:
    """Teacher flow: latest score of every student, and topics to re-teach.

    Only students the teacher may see (user.can_view_student) are listed.

    Args:
        store: the loaded DataStore.
        user: the logged-in Teacher.
    Complexity: O(q * s * (a + n)) for q quizzes and s students.
    """
    course_ids = {course.course_id for course in courses_for(store, user)}
    quizzes = [quiz for quiz in store.quizzes.values()
               if quiz.course_id in course_ids]
    quiz = choose_from("Quiz results", quizzes, lambda q: f"{q.quiz_id} {q.title}")
    if quiz is None:
        return
    course = store.courses[quiz.course_id]
    print(f"\n{quiz.quiz_id} {quiz.title}")
    class_results = [quiz_result_row(store, quiz, student_id)
                     for student_id in sorted(course.enrolled)
                     if user.can_view_student(student_id, store.courses)]
    print_class_topics(merge_topic_results(
        [result for result in class_results if result is not None]))


def quiz_result_row(store: DataStore, quiz, student_id: str):
    """Print one student's latest score on a quiz.

    Args:
        store: the loaded DataStore.
        quiz: the Quiz.
        student_id: the student.
    Returns:
        their {topic: (correct, total)}, or None if they have not attempted it.
    Complexity: O(a + n) for a attempts and n questions.
    """
    attempt = latest_attempts(store, student_id).get(quiz.quiz_id)
    name = store.users[student_id].name
    if attempt is None:
        print(f"  {student_id} {name:<18} not attempted")
        return None
    print(f"  {student_id} {name:<18} {attempt['score']}/{quiz.max_score}")
    return quiz.grade_attempt(attempt["answers"])[1]


def print_class_topics(class_results: dict) -> None:
    """Show the whole class's topic scores and the weakest topics.

    Args:
        class_results: merged {topic: (correct, total)} for the class.
    Complexity: O(t log t) for t topics.
    """
    if not class_results:
        print("No attempts yet, so no topic results.")
        return
    print("Class results by topic:")
    print_topic_table(class_results)
    weak = weak_topics(class_results)
    print("Topics to re-teach: " + (", ".join(weak) if weak else "none"))


# ------------------------------------------------- assignments (Part 8)

def assignment_status(assignment, submission) -> str:
    """Describe where a student is with one assignment.

    Args:
        assignment: the Assignment.
        submission: their Submission, or None if they have not submitted.
    Returns:
        text such as "marked 9/10" or "not submitted (deadline passed)".
    Complexity: O(1).
    """
    if submission is None:
        if assignment.is_open(datetime.now()):
            return "not submitted"
        return "not submitted (deadline passed)"
    late = " (late)" if submission.is_late(assignment) else ""
    if submission.marks is None:
        return f"submitted{late}, waiting for marks"
    return f"marked {submission.marks}/{assignment.max_marks}{late}"


def show_my_assignments(store: DataStore, user) -> None:
    """Student flow: status of every assignment, then submit a pending one.

    Args:
        store: the loaded DataStore.
        user: the logged-in Student.
    Complexity: O(a log a) for a assignments.
    """
    course_ids = {course.course_id for course in courses_for(store, user)}
    mine = sorted((a for a in store.assignments.values()
                   if a.course_id in course_ids), key=lambda a: a.deadline)
    if not mine:
        print("You have no assignments.")
        return
    print("\nYour assignments")
    for assignment in mine:
        submission = store.submissions.get((user.user_id, assignment.assignment_id))
        print(f"  {assignment.assignment_id} {assignment.title} "
              f"(due {format_datetime(assignment.deadline)}): "
              f"{assignment_status(assignment, submission)}")
        if submission is not None and submission.feedback:
            print(f"      feedback: {submission.feedback}")
    submit_pending(store, user, course_ids)


def submit_pending(store: DataStore, user, course_ids: set) -> None:
    """Let a student hand in one assignment they have not submitted yet.

    Args:
        store: the loaded DataStore.
        user: the logged-in Student.
        course_ids: the student's course IDs.
    Complexity: O(a log a) for a assignments.
    """
    pending = [a for a in store.assignments.values()
               if a.course_id in course_ids
               and (user.user_id, a.assignment_id) not in store.submissions]
    assignment = choose_from("Submit an assignment",
                             sorted(pending, key=lambda a: a.deadline),
                             lambda a: f"{a.assignment_id} {a.title}")
    if assignment is None:
        return
    text = ask_text("Type your answer (one line): ")
    submission = submit_work(store.submissions, assignment, user.user_id,
                             text, datetime.now())
    print("Submitted." + (" Note: this is after the deadline, so it is marked late."
                          if submission.is_late(assignment) else ""))


def mark_submissions(store: DataStore, user) -> None:
    """Teacher flow: choose an assignment, then mark one submission.

    Args:
        store: the loaded DataStore.
        user: the logged-in Teacher.
    Complexity: O(a + s log s) for a assignments and s submissions.
    """
    course_ids = {course.course_id for course in courses_for(store, user)}
    assignment = choose_from(
        "Mark submissions",
        [a for a in store.assignments.values() if a.course_id in course_ids],
        lambda a: f"{a.assignment_id} {a.title} (out of {a.max_marks})")
    if assignment is None:
        return
    submissions = sorted(
        (s for s in store.submissions.values()
         if s.assignment_id == assignment.assignment_id
         and user.can_view_student(s.student_id, store.courses)),
        key=lambda s: s.student_id)
    submission = choose_from(f"Submissions for {assignment.assignment_id}",
                             submissions,
                             lambda s: f"{s.student_id} {store.users[s.student_id].name}: "
                                       f"{assignment_status(assignment, s)}")
    if submission is not None:
        enter_marks(assignment, submission)


def enter_marks(assignment, submission) -> None:
    """Show a submission and ask the teacher for marks and feedback.

    The marks go through the Submission.marks property, which only accepts
    0..max_marks (ask_int already keeps the number in that range).

    Args:
        assignment: the Assignment.
        submission: the Submission being marked.
    Complexity: O(1).
    """
    print(f"\nAnswer from {submission.student_id}: {submission.text}")
    submission.marks = ask_int(f"Marks (0-{assignment.max_marks}): ",
                               0, assignment.max_marks)
    feedback = ask_text("Feedback (Enter to keep the old one): ", allow_empty=True)
    if feedback:
        submission.feedback = feedback
    print(f"Saved: {submission.marks}/{assignment.max_marks}.")


# --------------------------------------------------- admin menu (Part 8)

def list_accounts(store: DataStore, user) -> None:
    """Admin flow: print every account, with each student's courses.

    Args:
        store: the loaded DataStore.
        user: the logged-in Admin.
    Complexity: O(u log u + u * c) for u users and c courses.
    """
    print("\nAccounts")
    for account in accounts_by_role(store.users):
        line = f"  {account.describe()}"
        if account.role == "student":
            ids = [c.course_id for c in store.courses_for_student(account.user_id)]
            line += f"  courses: {', '.join(ids) or 'none'}"
        print(line)


def create_account_menu(store: DataStore, user) -> None:
    """Admin flow: ask for a role and a name, then make the account.

    Args:
        store: the loaded DataStore.
        user: the logged-in Admin.
    Complexity: O(u) for u users.
    """
    roles = ["student", "teacher", "admin"]
    role = roles[ask_choice("Role of the new account", roles) - 1]
    name = ask_text("Full name: ")
    account = create_account(store.users, role, name)
    print(f"Created {account.describe()}. They log in with {account.user_id}.")


def enroll_student_menu(store: DataStore, user) -> None:
    """Admin flow: choose a course, then a student who is not in it yet.

    Args:
        store: the loaded DataStore.
        user: the logged-in Admin.
    Complexity: O(c + u log u) for c courses and u users.
    """
    course = choose_from("Enroll into which course?", list(store.courses.values()),
                         lambda c: f"{c.course_id} {c.title} ({len(c.enrolled)} students)")
    if course is None:
        return
    student = choose_from(f"Students not in {course.course_id}",
                          students_not_in(store.users, course),
                          lambda s: f"{s.user_id} {s.name}")
    if student is None:
        return
    enroll_student(store.users, store.courses, student.user_id, course.course_id)
    print(f"{student.name} is now enrolled in {course.course_id}.")


def save_data(store: DataStore, user=None) -> bool:
    """Write every record to data/processed/ (menu item and exit step).

    Args:
        store: the loaded DataStore.
        user: the logged-in user (not needed; kept so every handler has
            the same call).
    Returns:
        True if saved, False if a file could not be written.
    Complexity: O(N) for N records.
    """
    try:
        store.save()
    except DataFileError as error:
        print(f"Could not save the data: {error}")
        return False
    print(f"Data saved to {PROCESSED_DIR.parent.name}/{PROCESSED_DIR.name}/.")
    return True


def coming_later(part: str):
    """Make a handler for a menu line that a later part will build.

    Args:
        part: e.g. "Part 8".
    Returns:
        a handler function that only prints a short message.
    Complexity: O(1).
    """
    return lambda store, user: print(f"This option is added in {part}.")


# Every menu line from users.py -> the function that runs it.
MENU_ACTIONS = {
    "My courses and materials": show_courses,
    "Take a quiz": take_quiz,
    "Practice questions": practice_questions,
    "My assignments": show_my_assignments,
    "My progress and revision tips": show_progress,
    "Quiz results": show_quiz_results,
    "Mark submissions": mark_submissions,
    "Class report": coming_later("Part 11"),
    "List accounts": list_accounts,
    "Create an account": create_account_menu,
    "Enroll a student": enroll_student_menu,
    "Save data": save_data,
}


# ---------------------------------------------------------------- main loop

def login(store: DataStore):
    """Ask for a user ID until it matches an account, or the user quits.

    Args:
        store: the loaded DataStore.
    Returns:
        the logged-in User, or None if the user typed Q.
    Complexity: O(1) per attempt (dict lookup).
    """
    while True:
        user_id = ask_text("\nUser ID (e.g. S01, T01, A01) or Q to quit: ")
        if user_id.upper() == "Q":
            return None
        try:
            return find_user(store.users, user_id)
        except LMSError as error:
            print(error)


def menu_loop(store: DataStore, user) -> None:
    """Show the user's own menu until they log out.

    The same code serves every role: the options come from
    user.menu_options() and the work from MENU_ACTIONS (polymorphism).

    Args:
        store: the loaded DataStore.
        user: the logged-in User.
    Complexity: O(1) per choice, plus the work of the chosen handler.
    """
    print(f"\nWelcome, {user.describe()}")
    while True:
        options = user.menu_options()
        line = options[ask_choice(f"{user.role.title()} menu", options) - 1]
        if line == LOG_OUT:
            print(f"Goodbye, {user.name}.")
            return
        try:
            MENU_ACTIONS[line](store, user)
        except LMSError as error:
            print(f"Sorry: {error}")


def run() -> None:
    """Start the program: load the data, then log users in one after another.

    Typing Q at login, or reaching the end of the input (Ctrl+D), quits.
    Either way the data is saved before the program ends (Part 8).

    Complexity: O(N) to load N records, then O(1) per menu choice.
    """
    show_banner()
    store = DataStore()
    try:
        store.load()
    except LMSError as error:
        print(f"Could not load the data: {error}")
        return
    try:
        user = login(store)
        while user is not None:
            menu_loop(store, user)
            user = login(store)
    except (EOFError, KeyboardInterrupt):
        print()
    save_data(store)
    print("Thank you for using ALPHA LMS.")


if __name__ == "__main__":
    run()
