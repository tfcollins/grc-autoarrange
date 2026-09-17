# Installation Guide

## Prerequisites

- **Python 3.8+**
- **GNU Radio 3.8+ / 3.10+** (with GNU Radio Companion installed)
- **Node.js runtime** (`node` binary available on your `PATH`).

!!! tip "Node.js Requirement"
    `grc-autoarrange` uses the **Eclipse Layout Kernel (ELK)**. The full ELK engine bundle (`elk.bundled.js`) is self-contained inside the Python package, meaning **you do not need to run `npm install`**. You only need the standard `node` interpreter installed on your system.

---

## Which Python Should I Install Into?

GNU Radio's Python bindings are compiled extensions. They can only be imported by the interpreter
they were built for:

| GNU Radio install | Interpreter that owns it |
|---|---|
| apt / dnf / pacman package | system `python3` (e.g. `/usr/bin/python3`) |
| conda / radioconda | the conda environment's `python` |
| PyBOMBS / source build | whatever `-DPYTHON_EXECUTABLE` pointed at |

The headless formatter (`grc-autoarrange -i file.grc`) works from any Python 3.8+. Only the
`--gui` mode needs to import GNU Radio.

!!! tip "Automatic hand-off"
    If `grc-autoarrange --gui` is run from a Python that cannot import `gnuradio`, it reads the
    shebang of the `gnuradio-companion` launcher on your `PATH` and re-launches itself under that
    interpreter, exposing only its own package via `PYTHONPATH`. No additional packages need to be
    installed there: the sole runtime dependency, `pyyaml`, is already required by GNU Radio Companion.
    Set `GRC_AUTOARRANGE_NO_REEXEC=1` to disable this behaviour.

---

## Installing

### Recommended: pipx with system site-packages

```bash
git clone https://github.com/tfcollins/grc-autoarrange.git
cd grc-autoarrange
pipx install --system-site-packages .
```

This gives the tool its own isolated environment while still letting it import the distro's
GNU Radio directly, so no re-launch is needed.

!!! warning "PEP 668 on Debian / Ubuntu"
    `pip install --user .` against the system Python fails with an *externally-managed-environment*
    error on Debian 12+, Ubuntu 23.04+ and similar. Use `pipx` as shown above, or a virtual
    environment as below, rather than `--break-system-packages`.

### Alternative: a virtual environment that can see GNU Radio

```bash
python3 -m venv --system-site-packages ~/.venvs/grc-autoarrange
~/.venvs/grc-autoarrange/bin/pip install .
```

Use the `python3` that owns GNU Radio (see table above) to create the venv.

### Conda / radioconda

Activate the environment that contains GNU Radio, then:

```bash
pip install .
```

### Editable Development Installation

If you are developing or customizing the layout rules:

```bash
pip install -e .
```

Any interpreter works for running the unit tests; use `--gui` from a GNU Radio-capable one, or rely
on the automatic hand-off described above.

---

## Verifying the Installation

Verify that the CLI executable is available in your shell:

```bash
grc-autoarrange --help
```

You should see the help menu with options like `--gui`, `-i/--in-place`, `-d/--direction`, and spacing controls.
