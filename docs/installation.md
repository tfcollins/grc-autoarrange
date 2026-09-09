# Installation Guide

## Prerequisites

- **Python 3.8+**
- **GNU Radio 3.8+ / 3.10+** (with GNU Radio Companion installed)
- **Node.js runtime** (`node` binary available on your `PATH`).

!!! tip "Node.js Requirement"
    `grc-autoarrange` uses the **Eclipse Layout Kernel (ELK)**. The full ELK engine bundle (`elk.bundled.js`) is self-contained inside the Python package, meaning **you do not need to run `npm install`**. You only need the standard `node` interpreter installed on your system.

---

## Installing via Pip

### User Installation (Recommended)

```bash
git clone https://github.com/tfcollins/grc-autoarrange.git
cd grc-autoarrange
pip install --user .
```

### Editable Development Installation

If you are developing or customizing the layout rules:

```bash
pip install --user -e .
```

---

## Verifying the Installation

Verify that the CLI executable is available in your shell:

```bash
grc-autoarrange --help
```

You should see the help menu with options like `--gui`, `-i/--in-place`, `-d/--direction`, and spacing controls.
