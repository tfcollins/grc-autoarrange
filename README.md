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

## 📖 Live Documentation & Interactive Demo

👉 **[https://tfcollins.github.io/grc-autoarrange/](https://tfcollins.github.io/grc-autoarrange/)**

Visit our interactive documentation site to view a **live interactive animation** of tangled flowgraph cables and unaligned blocks being untangled and snapped into an optimal layered DAG layout in real-time.

---

## ⚡ Features

- **GNU Radio Companion Integration:**
  - Adds **Auto Arrange Flowgraph** directly into GRC's `Edit` menu, `Tools` menu, and toolbar.
  - Shortcut: <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd>.
  - Full **Undo / Redo** support (<kbd>Ctrl</kbd> + <kbd>Z</kbd> / <kbd>Ctrl</kbd> + <kbd>Y</kbd>).
  - Selection support: Select specific blocks to rearrange only the selected subgraph.
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
# Clone the repository
git clone https://github.com/tfcollins/grc-autoarrange.git
cd grc-autoarrange

# Install in editable mode or user environment
pip install --user .
```

*Prerequisite: `node` (Node.js runtime) available on PATH.*

---

## 🚀 Usage

### 1. Launching GRC with Auto-Arrange

Launch GNU Radio Companion with the Auto-Arrange addon enabled:

```bash
grc-autoarrange --gui [flowgraph.grc]
```

Inside GRC:
- Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd> or click **Edit &rarr; Auto Arrange Flowgraph**.
- To format a subset of blocks, select them on canvas and trigger Auto-Arrange.

### 2. Standalone CLI Formatter

Format a `.grc` flowgraph file in-place:
```bash
grc-autoarrange -i my_flowgraph.grc
```

Format to a new file:
```bash
grc-autoarrange input.grc -o output.grc
```

Change layout direction or spacing:
```bash
grc-autoarrange input.grc -o output.grc --direction RIGHT --node-spacing 60 --layer-spacing 80
```

Dry run / preview:
```bash
grc-autoarrange --dry-run my_flowgraph.grc
```

### 3. Python API

```python
from grc_autoarrange import load_grc_file, save_grc_file, LayoutPlanner

data = load_grc_file("flowgraph.grc")
planner = LayoutPlanner()
new_coords = planner.arrange_flowgraph_data(data)

# Update coordinates and save
for block in data.get("blocks", []):
    name = block.get("name")
    if name in new_coords:
        block["states"]["coordinate"] = list(new_coords[name])

save_grc_file(data, "flowgraph_arranged.grc")
```

---

## 📄 License

GNU General Public License v2 or later (GPL-2.0-or-later).
