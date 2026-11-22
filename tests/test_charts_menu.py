"""Tests for the teacher's "Progress charts" menu item (main.show_charts).

The chart drawing itself is tested through charts.py; here make_all_charts,
the menu answer and the image viewer are replaced, so no real files or
windows are opened.
"""

import subprocess
from pathlib import Path

import main
from exceptions import ValidationError
from users import Admin, Student, Teacher


def test_only_teachers_see_progress_charts():
    assert "Progress charts" in Teacher("T01", "B").menu_options()
    assert "Progress charts" not in Student("S01", "A").menu_options()
    assert "Progress charts" not in Admin("A01", "C").menu_options()
    assert main.MENU_ACTIONS["Progress charts"] is main.show_charts


def fake_paths(tmp_path):
    folder = tmp_path / "outputs" / "figures"
    return [folder / name for name in ("quiz_averages.png", "assignment_completion.png",
                                       "score_histogram.png", "topic_heatmap.png")]


def test_show_charts_lists_files_and_skips_opening(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(main, "make_all_charts", lambda store: fake_paths(tmp_path))
    monkeypatch.setattr(main, "ask_choice", lambda title, options: 2)   # "No"
    opened = []
    monkeypatch.setattr(main, "open_file", lambda path: opened.append(path) or True)
    main.show_charts(None, Teacher("T01", "B"))
    out = capsys.readouterr().out
    assert "outputs/figures/quiz_averages.png" in out
    assert "outputs/figures/topic_heatmap.png" in out
    assert opened == []


def test_show_charts_opens_all_four(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "make_all_charts", lambda store: fake_paths(tmp_path))
    monkeypatch.setattr(main, "ask_choice", lambda title, options: 1)   # "Yes"
    opened = []
    monkeypatch.setattr(main, "open_file", lambda path: opened.append(path) or True)
    main.show_charts(None, Teacher("T01", "B"))
    assert [p.name for p in opened] == [p.name for p in fake_paths(tmp_path)]


def test_show_charts_without_viewer_prints_hint(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(main, "make_all_charts", lambda store: fake_paths(tmp_path))
    monkeypatch.setattr(main, "ask_choice", lambda title, options: 1)
    monkeypatch.setattr(main, "open_file", lambda path: False)
    main.show_charts(None, Teacher("T01", "B"))
    assert "No image viewer found" in capsys.readouterr().out


def test_show_charts_with_no_data_prints_error(monkeypatch, capsys):
    def no_data(store):
        raise ValidationError("There are no quiz attempts to chart.")
    monkeypatch.setattr(main, "make_all_charts", no_data)
    main.show_charts(None, Teacher("T01", "B"))
    assert "Could not draw the charts" in capsys.readouterr().out


def test_open_file_returns_false_when_viewer_fails(monkeypatch):
    def broken(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "open")
    monkeypatch.setattr(main.sys, "platform", "darwin")
    monkeypatch.setattr(main.subprocess, "run", broken)
    assert main.open_file(Path("missing.png")) is False


def test_open_file_returns_false_without_viewer_program(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("xdg-open")
    monkeypatch.setattr(main.sys, "platform", "linux")
    monkeypatch.setattr(main.subprocess, "run", missing)
    assert main.open_file(Path("missing.png")) is False
