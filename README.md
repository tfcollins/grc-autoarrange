<p align="center">
  <img src="docs/assets/logo.svg" alt="GRC Auto-Arrange Logo" width="200"/>
</p>

<h1 align="center">GRC Auto-Arrange</h1>

<p align="center">
  <strong>Intelligent, automated block placement and flowgraph beautifier for GNU Radio Companion (GRC)</strong><br/>
  Powered by the <strong>Eclipse Layout Kernel (ELK)</strong> layered Sugiyama layout engine.
</p>

<p align="center">
  <a href="https://github.com/tfcollins/grc-autoarrange"><img src="https://img.shields.io/badge/GNU%20Radio-3.8%20%7C%203.10-blue.svg?style=flat-square&logo=gnuradio" alt="GNU Radio Version"/></a>
  <a href="https://github.com/tfcollins/grc-autoarrange"><img src="https://img.shields.io/badge/Layout%20Engine-Eclipse%20ELK-orange.svg?style=flat-square" alt="ELK Engine"/></a>
  <a href="https://github.com/tfcollins/grc-autoarrange"><img src="https://img.shields.io/badge/Grid-8px%20Snap-emerald.svg?style=flat-square" alt="Grid Snapping"/></a>
  <a href="https://tfcollins.github.io/grc-autoarrange/"><img src="https://img.shields.io/badge/Docs-GitHub%20Pages-indigo.svg?style=flat-square" alt="Documentation"/></a>
  <a href="https://github.com/tfcollins/grc-autoarrange/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-GPLv2%2B-green.svg?style=flat-square" alt="License"/></a>
</p>

---

## 📸 GNU Radio Companion Before & After

| Before Auto-Arrange (Messy) | After Auto-Arrange (`Ctrl+Shift+A`) |
| :---: | :---: |
| <img src="docs/assets/grc_window_before.png" alt="Before Auto-Arrange" width="480"/> | <img src="docs/assets/grc_window_after.png" alt="After Auto-Arrange" width="480"/> |
| *Scattered blocks, backwards routing, overlapping wires* | *Clean layered DAG, variables in header banner, 8px grid aligned* |

---

## 🎛️ Configurable Block Spacing

Easily adjust block and layer spacing either via the GRC graphical settings dialog or via CLI flags:

<p align="center">
  <img src="docs/assets/grc_settings_dialog.png" alt="Settings Dialog" width="380"/>
</p>

| Compact Spacing (`--spacing 24`) | Spacious Layout (`--spacing 96`) |
| :---: | :---: |
| <img src="docs/assets/grc_spacing_compact.png" alt="Compact Spacing" width="480"/> | <img src="docs/assets/grc_spacing_spacious.png" alt="Spacious Spacing" width="480"/> |
| *High density layout for large complex flowgraphs* | *Generous spacing for wide multi-branch pipelines* |

---

## 📖 Live Documentation & Interactive Demo

👉 **[https://tfcollins.github.io/grc-autoarrange/](https://tfcollins.github.io/grc-autoarrange/)**

Visit our interactive documentation site to view a **live interactive animation** of tangled flowgraph cables and unaligned blocks being untangled and snapped into an optimal layered DAG layout in real-time.

---

## ⚡ Features

- **GNU Radio Companion Integration:**
  - Adds **Auto Arrange Flowgraph** into GRC's `Edit` and `Tools` menus and toolbar.
  - Shortcut: <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd>.
  - Full **Undo / Redo** support (<kbd>Ctrl</kbd> + <kbd>Z</kbd> / <kbd>Ctrl</kbd> + <kbd>Y</kbd>).
  - Selection support: Select specific blocks to rearrange only the selected subgraph.
- **Configurable Spacing & Preferences:**
  - Dedicated GTK3 Settings Dialog (**Edit &rarr; Auto Arrange Settings...**).
  - Persistent user preferences saved to `~/.config/gnuradio/grc_autoarrange.json`.
- **Smart Block Categorization:**
  - **Header & Variables Banner:** Variables (`variable`, `variable_qtgui_*`, `import`, `parameter`, etc.) are cleanly arranged in a neat header grid above the flowgraph.
  - **Signal Processing DAG:** Processing blocks (sources, filters, arithmetic, sinks) are layered left-to-right using ELK's port-constrained crossing minimization and Brandes-Köpf coordinate assignment.
  - **Disconnected / Floating Blocks:** Placed neatly below the main graph.
- **Grid Snapping:** Automatically snaps all block coordinates to GRC's standard 8px grid.
- **Zero External NPM Dependencies:** The standalone ELK engine bundle is self-contained within the package and runs automatically using your system's Node.js runtime.
- **Standalone CLI & Batch Formatter:** Format any `.grc` file headlessly or in CI/CD pre-commit hooks.

---

## 📦 Installation

```bash
git clone https://github.com/tfcollins/grc-autoarrange.git
cd grc-autoarrange

# Recommended: isolated install that can still see your system GNU Radio
pipx install --system-site-packages .
```

*Prerequisite: `node` (Node.js runtime) available on PATH.*

**Which Python?** GNU Radio's Python bindings only import from the interpreter they were built for
(for apt/dnf packages that is the system `python3`; for conda it is the env's `python`). The headless
formatter works from any Python, but `--gui` must reach GNU Radio. You have two options:

- Install into a Python that can see GNU Radio, e.g. `pipx install --system-site-packages .` or a venv created with `python3 -m venv --system-site-packages`.
- Install anywhere and let the tool handle it: if `gnuradio` is not importable, `grc-autoarrange --gui` finds `gnuradio-companion` on `PATH` and re-launches itself under that interpreter. No extra dependencies are required there, since GNU Radio already ships `pyyaml`.

On Debian/Ubuntu, `pip install --user .` against the system Python is blocked by PEP 668; use `pipx` as shown above instead.

---

## 🚀 Usage

### 1. Launching GRC with Auto-Arrange

Launch GNU Radio Companion with the Auto-Arrange addon enabled:

```bash
grc-autoarrange --gui [flowgraph.grc]
```

Inside GRC:
- Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd> or click **Edit &rarr; Auto Arrange Flowgraph**.
- Configure spacing via **Edit &rarr; Auto Arrange Settings...**.

### 2. Standalone CLI Formatter

Format a `.grc` flowgraph file in-place:
```bash
grc-autoarrange -i my_flowgraph.grc --spacing 60
```

Format to a new file:
```bash
grc-autoarrange input.grc -o output.grc --spacing 72
```

Save default spacing preferences:
```bash
grc-autoarrange --spacing 72 --save-defaults
```

### 3. Python API

```python
from grc_autoarrange import LayoutPlanner, LayoutConfig

# Custom spacing configuration
config = LayoutConfig(block_spacing=64)
planner = LayoutPlanner(config=config)
new_coords = planner.arrange_flowgraph_data(data)
```

---

## 📄 License

GNU General Public License v2 or later (GPL-2.0-or-later).
