"""Edge-case tests for users.py and storage.py.

Owner: Ashbar Hussain (Part 15)
Cases: empty input, one element, duplicates, large input, invalid input,
missing file, malformed JSON.
"""

import json

import pytest

from courses import Course
from exceptions import DataFileError, DuplicateError, NotFoundError, ValidationError
from storage import (DataStore, data_dir, load_csv, load_json, save_csv,
                     save_json, RAW_DIR)
from users import Admin, Student, Teacher, User, find_user, user_from_dict


# ---------- users ----------

def test_user_is_abstract():
    """A plain User cannot be created."""
    with pytest.raises(TypeError):
        User("S01", "Ali")


@pytest.mark.parametrize("user_id, name", [("", "Ali"), ("S01", ""),
                                           ("   ", "Ali"), (None, "Ali"),
                                           ("S01", None), (5, "Ali")])
def test_user_rejects_empty_or_non_text(user_id, name):
    """Empty, blank or non-text ID/name is refused."""
    with pytest.raises(ValidationError):
        Student(user_id, name)


def test_user_id_is_upper_case_and_trimmed():
    """IDs are normalised so s01 and S01 are the same account."""
    assert Student(" s01 ", " Ali ").user_id == "S01"
    assert Student("s01", " Ali ").name == "Ali"


def test_user_properties_are_read_only():
    """user_id and name cannot be assigned."""
    student = Student("S01", "Ali")
    with pytest.raises(AttributeError):
        student.user_id = "S02"
    with pytest.raises(AttributeError):
        student.name = "Bob"


def test_roles_and_menus_differ():
    """Each role overrides role and menu_options (polymorphism)."""
    people = [Student("S01", "A"), Teacher("T01", "B"), Admin("A01", "C")]
    assert [p.role for p in people] == ["student", "teacher", "admin"]
    menus = [tuple(p.menu_options()) for p in people]
    assert len(set(menus)) == 3
    assert all(menu[-1] == "Log out" for menu in menus)


def test_student_can_view_only_self():
    """A student sees only their own records, whatever the input looks like."""
    student = Student("S01", "Ali")
    assert student.can_view_student("s01", {})
    assert not student.can_view_student("S02", {})
    assert not student.can_view_student("", {})
    assert not student.can_view_student(None, {})


def test_admin_can_view_everyone():
    """An admin may see any student, even an unknown one."""
    assert Admin("A01", "Root").can_view_student("S99", {})


def test_teacher_view_with_no_courses_and_one_course():
    """Empty courses -> False; one taught course with the student -> True."""
    teacher = Teacher("T01", "Sara")
    assert not teacher.can_view_student("S01", {})
    mine = Course("C101", "AI", "T01")
    mine.enroll("S01")
    other = Course("C102", "DS", "T02")
    other.enroll("S02")
    courses = {"C101": mine, "C102": other}
    assert teacher.can_view_student("s01", courses)
    assert not teacher.can_view_student("S02", courses)


def test_user_to_dict_round_trip():
    """to_dict and user_from_dict are inverse."""
    teacher = Teacher("T01", "Sara")
    copy = user_from_dict(teacher.to_dict())
    assert isinstance(copy, Teacher) and copy.to_dict() == teacher.to_dict()


@pytest.mark.parametrize("record", [
    None, [], "S01", {}, {"user_id": "S01", "name": "Ali"},
    {"user_id": "S01", "name": "Ali", "role": "dean"},
    {"user_id": "S01", "name": "Ali", "role": ""},
    {"user_id": "", "name": "Ali", "role": "student"},
])
def test_user_from_dict_invalid(record):
    """Bad records raise ValidationError, not a crash."""
    with pytest.raises(ValidationError):
        user_from_dict(record)


def test_user_from_dict_role_is_case_insensitive():
    """"STUDENT" still builds a Student."""
    record = {"user_id": "S01", "name": "Ali", "role": "STUDENT"}
    assert isinstance(user_from_dict(record), Student)


def test_find_user_cases():
    """Case-insensitive lookup; empty dict and unknown IDs raise NotFoundError."""
    users = {"S01": Student("S01", "Ali")}
    assert find_user(users, " s01 ").name == "Ali"
    with pytest.raises(NotFoundError):
        find_user(users, "S02")
    with pytest.raises(NotFoundError):
        find_user({}, "S01")
    with pytest.raises(NotFoundError):
        find_user(users, "")


def test_find_user_in_large_dict():
    """Lookup works in a dict of 10,000 users."""
    users = {f"S{i}": Student(f"S{i}", f"N{i}") for i in range(10000)}
    assert find_user(users, "s9999").user_id == "S9999"


# ---------- json / csv files ----------

def test_json_round_trip_with_unicode(tmp_path):
    """Saved JSON loads back unchanged, including non-ASCII text."""
    path = tmp_path / "a.json"
    data = [{"name": "Zoë", "n": 1}]
    save_json(path, data)
    assert load_json(path) == data


def test_json_empty_list(tmp_path):
    """An empty list is valid data."""
    save_json(tmp_path / "e.json", [])
    assert load_json(tmp_path / "e.json") == []


def test_load_json_missing_file(tmp_path):
    """A missing file raises DataFileError."""
    with pytest.raises(DataFileError):
        load_json(tmp_path / "nope.json")


@pytest.mark.parametrize("text", ["{bad", "", "[1, 2,", "not json"])
def test_load_json_malformed(tmp_path, text):
    """Malformed or empty JSON raises DataFileError."""
    path = tmp_path / "bad.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(DataFileError):
        load_json(path)


def test_load_json_bad_encoding(tmp_path):
    """Bytes that are not UTF-8 raise DataFileError."""
    path = tmp_path / "b.json"
    path.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(DataFileError):
        load_json(path)


def test_save_json_unserialisable_leaves_no_files(tmp_path):
    """Data JSON cannot encode raises DataFileError and leaves no temp file."""
    path = tmp_path / "x.json"
    with pytest.raises(DataFileError):
        save_json(path, {"a": {1, 2}})
    assert list(tmp_path.iterdir()) == []


def test_failed_save_keeps_old_file(tmp_path):
    """A failed save never damages the previous good file."""
    path = tmp_path / "x.json"
    save_json(path, [1])
    with pytest.raises(DataFileError):
        save_json(path, [object()])
    assert load_json(path) == [1]
    assert [p.name for p in tmp_path.iterdir()] == ["x.json"]


def test_save_json_unwritable_folder(tmp_path):
    """A folder path blocked by a file raises DataFileError."""
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(DataFileError):
        save_json(blocker / "sub" / "a.json", [])


def test_save_creates_missing_folder(tmp_path):
    """Missing parent folders are created."""
    path = tmp_path / "a" / "b" / "c.json"
    save_json(path, [1])
    assert load_json(path) == [1]


def test_csv_round_trip_with_commas_quotes_newlines(tmp_path):
    """Tricky text survives a CSV round trip."""
    path = tmp_path / "a.csv"
    rows = [{"id": "1", "text": 'say "hi", ok\nnew line'}]
    save_csv(path, rows, ["id", "text"])
    assert load_csv(path) == rows


def test_csv_header_only_and_empty_rows(tmp_path):
    """No rows gives an empty list; header is still written."""
    path = tmp_path / "a.csv"
    save_csv(path, [], ["id", "text"])
    assert load_csv(path) == []
    assert path.read_text().strip() == "id,text"


def test_csv_zero_byte_file(tmp_path):
    """A completely empty file loads as no rows."""
    path = tmp_path / "z.csv"
    path.write_text("")
    assert load_csv(path) == []


def test_load_csv_missing_file(tmp_path):
    """A missing CSV raises DataFileError."""
    with pytest.raises(DataFileError):
        load_csv(tmp_path / "nope.csv")


def test_load_csv_short_and_long_rows(tmp_path):
    """Missing values become '', extra values are dropped."""
    path = tmp_path / "r.csv"
    path.write_text("a,b\n1\n1,2,3\n", encoding="utf-8")
    assert load_csv(path) == [{"a": "1", "b": ""}, {"a": "1", "b": "2"}]


def test_save_csv_unknown_column(tmp_path):
    """A row with a column missing from fieldnames raises DataFileError."""
    with pytest.raises(DataFileError):
        save_csv(tmp_path / "a.csv", [{"zzz": 1}], ["a"])


def test_csv_large_input(tmp_path):
    """10,000 rows round-trip correctly."""
    path = tmp_path / "big.csv"
    rows = [{"id": str(i), "v": f"value {i}"} for i in range(10000)]
    save_csv(path, rows, ["id", "v"])
    loaded = load_csv(path)
    assert len(loaded) == 10000 and loaded[-1] == rows[-1]


# ---------- DataStore ----------

def sample_folder(tmp_path):
    """Write a tiny valid data set and return its folder."""
    save_json(tmp_path / "users.json", [
        {"user_id": "T01", "name": "Sara", "role": "teacher"},
        {"user_id": "S01", "name": "Ali", "role": "student"}])
    save_csv(tmp_path / "courses.csv",
             [{"course_id": "C1", "title": "AI", "teacher_id": "T01"}],
             ["course_id", "title", "teacher_id"])
    save_csv(tmp_path / "enrollments.csv",
             [{"student_id": "S01", "course_id": "C1"}],
             ["student_id", "course_id"])
    save_csv(tmp_path / "materials.csv", [],
             ["material_id", "course_id", "title", "topic", "file_name"])
    save_json(tmp_path / "quizzes.json", [])
    save_json(tmp_path / "attempts.json", [])
    save_json(tmp_path / "assignments.json", [])
    save_csv(tmp_path / "submissions.csv", [],
             ["student_id", "assignment_id", "submitted_at", "text",
              "marks", "feedback"])
    return tmp_path


def test_new_store_is_empty():
    """A fresh DataStore has empty dicts and list."""
    store = DataStore()
    assert store.users == {} and store.courses == {} and store.attempts == []
    assert store.courses_for_student("S01") == []
    assert store.courses_for_teacher("T01") == []


def test_load_minimal_folder(tmp_path):
    """One user, one course, nothing else loads fine."""
    store = DataStore()
    store.load(sample_folder(tmp_path))
    assert set(store.users) == {"T01", "S01"}
    assert len(store.courses_for_student("S01")) == 1
    assert store.courses_for_student("S02") == []
    assert len(store.courses_for_teacher("T01")) == 1


def test_load_twice_does_not_duplicate(tmp_path):
    """Calling load() again starts from empty, so no DuplicateError."""
    folder = sample_folder(tmp_path)
    store = DataStore()
    store.load(folder)
    store.load(folder)
    assert len(store.users) == 2


def test_load_missing_file(tmp_path):
    """A missing data file raises DataFileError."""
    folder = sample_folder(tmp_path)
    (folder / "attempts.json").unlink()
    with pytest.raises(DataFileError):
        DataStore().load(folder)


def test_load_malformed_json(tmp_path):
    """Malformed users.json raises DataFileError."""
    folder = sample_folder(tmp_path)
    (folder / "users.json").write_text("{oops")
    with pytest.raises(DataFileError):
        DataStore().load(folder)


@pytest.mark.parametrize("content", ['{"a": 1}', '"text"', "[1, 2]", "null"])
def test_load_json_that_is_not_a_record_list(tmp_path, content):
    """JSON that is not a list of dicts raises DataFileError."""
    folder = sample_folder(tmp_path)
    (folder / "attempts.json").write_text(content)
    with pytest.raises(DataFileError):
        DataStore().load(folder)


def test_load_duplicate_user(tmp_path):
    """Two users with the same ID raise DuplicateError."""
    folder = sample_folder(tmp_path)
    save_json(folder / "users.json", [
        {"user_id": "T01", "name": "Sara", "role": "teacher"},
        {"user_id": "t01", "name": "Other", "role": "teacher"}])
    with pytest.raises(DuplicateError):
        DataStore().load(folder)


def test_load_duplicate_enrollment(tmp_path):
    """The same enrollment twice raises DuplicateError."""
    folder = sample_folder(tmp_path)
    row = {"student_id": "S01", "course_id": "C1"}
    save_csv(folder / "enrollments.csv", [row, row],
             ["student_id", "course_id"])
    with pytest.raises(DuplicateError):
        DataStore().load(folder)


def test_load_unknown_references(tmp_path):
    """Enrolling an unknown student or course raises ValidationError."""
    folder = sample_folder(tmp_path)
    save_csv(folder / "enrollments.csv",
             [{"student_id": "S99", "course_id": "C1"}],
             ["student_id", "course_id"])
    with pytest.raises(ValidationError):
        DataStore().load(folder)
    save_csv(folder / "enrollments.csv",
             [{"student_id": "S01", "course_id": "C9"}],
             ["student_id", "course_id"])
    with pytest.raises(ValidationError):
        DataStore().load(folder)


def test_load_course_with_unknown_teacher(tmp_path):
    """A course whose teacher does not exist is refused."""
    folder = sample_folder(tmp_path)
    save_csv(folder / "courses.csv",
             [{"course_id": "C1", "title": "AI", "teacher_id": "T77"}],
             ["course_id", "title", "teacher_id"])
    with pytest.raises(ValidationError):
        DataStore().load(folder)


def test_save_then_load_sample_data(tmp_path):
    """The real sample data survives save() then load()."""
    first = DataStore()
    first.load(RAW_DIR)
    first.save(tmp_path)
    second = DataStore()
    second.load(tmp_path)
    assert set(second.users) == set(first.users)
    assert {k: c.enrolled for k, c in second.courses.items()} == \
        {k: c.enrolled for k, c in first.courses.items()}
    assert set(second.submissions) == set(first.submissions)
    assert second.attempts == first.attempts


def test_save_empty_store_writes_all_files(tmp_path):
    """Saving an empty store still writes every file, and reloads."""
    DataStore().save(tmp_path)
    assert len(list(tmp_path.glob("*.*"))) == 8
    store = DataStore()
    store.load(tmp_path)
    assert store.users == {}


def test_saved_json_is_valid(tmp_path):
    """users.json written by save() is plain valid JSON."""
    store = DataStore()
    store.load(sample_folder(tmp_path / "in"))
    store.save(tmp_path / "out")
    data = json.loads((tmp_path / "out" / "users.json").read_text())
    assert {u["user_id"] for u in data} == {"T01", "S01"}


def test_large_store_round_trip(tmp_path):
    """1,000 students enrolled in one course save and reload."""
    store = DataStore()
    store.users["T01"] = Teacher("T01", "Sara")
    course = Course("C1", "AI", "T01")
    store.courses["C1"] = course
    for i in range(1000):
        user = Student(f"S{i:04d}", f"Student {i}")
        store.users[user.user_id] = user
        course.enroll(user.user_id)
    store.save(tmp_path)
    again = DataStore()
    again.load(tmp_path)
    assert len(again.courses["C1"].enrolled) == 1000


def test_data_dir_prefers_processed(monkeypatch, tmp_path):
    """data_dir() uses processed only when users.json is there."""
    import storage
    processed = tmp_path / "processed"
    processed.mkdir()
    monkeypatch.setattr(storage, "PROCESSED_DIR", processed)
    assert data_dir() == RAW_DIR
    (processed / "users.json").write_text("[]")
    assert data_dir() == processed
