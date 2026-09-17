"""Tests for the interpreter-detection and re-exec logic used by ``--gui``."""

import os
import stat
import sys
from pathlib import Path

import pytest

from grc_autoarrange import gui_addon


def _write_launcher(dirpath: Path, shebang: str) -> Path:
    exe = dirpath / "gnuradio-companion"
    exe.write_text(f"{shebang}\n# fake launcher\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    return exe


def _fake_python(dirpath: Path, name: str = "python3") -> Path:
    dirpath.mkdir(parents=True, exist_ok=True)
    py = dirpath / name
    py.write_text("#!/bin/sh\nexit 0\n")
    py.chmod(py.stat().st_mode | stat.S_IEXEC)
    return py


def test_find_interpreter_from_absolute_shebang(tmp_path, monkeypatch):
    interp = _fake_python(tmp_path / "bin_interp")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    _write_launcher(bindir, f"#!{interp}")
    monkeypatch.setenv("PATH", str(bindir))
    assert gui_addon.find_grc_interpreter() == str(interp)


def test_find_interpreter_from_env_shebang(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    interp = _fake_python(bindir, "python3")
    _write_launcher(bindir, "#!/usr/bin/env python3")
    monkeypatch.setenv("PATH", str(bindir))
    assert gui_addon.find_grc_interpreter() == str(interp)


def test_find_interpreter_returns_none_when_not_on_path(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    assert gui_addon.find_grc_interpreter() is None


def test_find_interpreter_returns_none_for_current_interpreter(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    _write_launcher(bindir, f"#!{sys.executable}")
    monkeypatch.setenv("PATH", str(bindir))
    assert gui_addon.find_grc_interpreter() is None


def test_find_interpreter_returns_none_for_binary_launcher(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    exe = bindir / "gnuradio-companion"
    exe.write_bytes(b"\x7fELF\x02\x01\x01")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", str(bindir))
    assert gui_addon.find_grc_interpreter() is None


def test_launch_reexecs_when_gnuradio_missing(tmp_path, monkeypatch):
    interp = _fake_python(tmp_path)
    calls = {}

    def fake_execve(path, argv, env):
        calls["path"] = path
        calls["argv"] = argv
        calls["env"] = env
        raise OSError("exec intercepted")

    monkeypatch.setattr(gui_addon, "gnuradio_importable", lambda: False)
    monkeypatch.setattr(gui_addon, "find_grc_interpreter", lambda: str(interp))
    monkeypatch.setattr(gui_addon.os, "execve", fake_execve)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.delenv(gui_addon.NO_REEXEC_ENV, raising=False)
    monkeypatch.setenv("PYTHONPATH", "/existing/path")

    with pytest.raises(OSError, match="exec intercepted"):
        gui_addon.launch_grc(["gnuradio-companion", "a.grc", "b.grc"])

    assert calls["path"] == str(interp)
    assert calls["argv"] == [str(interp), "-m", "grc_autoarrange", "--gui", "a.grc", "b.grc"]
    assert calls["env"][gui_addon.NO_REEXEC_ENV] == "1"

    entries = calls["env"]["PYTHONPATH"].split(os.pathsep)
    assert entries[-1] == "/existing/path"
    shim = Path(entries[0])
    link = shim / "grc_autoarrange"
    assert link.is_symlink()
    assert link.resolve() == Path(gui_addon.__file__).resolve().parent
    # Only our package is exposed to the foreign interpreter
    assert sorted(p.name for p in shim.iterdir()) == ["grc_autoarrange"]


def test_launch_errors_when_no_interpreter_found(monkeypatch, capsys):
    monkeypatch.setattr(gui_addon, "gnuradio_importable", lambda: False)
    monkeypatch.setattr(gui_addon, "find_grc_interpreter", lambda: None)
    monkeypatch.delenv(gui_addon.NO_REEXEC_ENV, raising=False)
    assert gui_addon.launch_grc(["gnuradio-companion"]) == 1
    err = capsys.readouterr().err
    assert "cannot import 'gnuradio'" in err
    assert "pipx install --system-site-packages" in err


def test_launch_does_not_loop_when_guard_set(monkeypatch, capsys):
    monkeypatch.setattr(gui_addon, "gnuradio_importable", lambda: False)
    monkeypatch.setattr(gui_addon, "find_grc_interpreter", lambda: pytest.fail("must not re-exec"))
    monkeypatch.setenv(gui_addon.NO_REEXEC_ENV, "1")
    assert gui_addon.launch_grc(["gnuradio-companion"]) == 1
    assert "cannot import 'gnuradio'" in capsys.readouterr().err


def test_shim_dir_reused_and_refreshed(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    first = gui_addon._package_shim_dir()
    # Stale link pointing elsewhere gets replaced
    link = first / "grc_autoarrange"
    link.unlink()
    link.symlink_to(tmp_path)
    second = gui_addon._package_shim_dir()
    assert second == first
    assert link.resolve() == Path(gui_addon.__file__).resolve().parent
