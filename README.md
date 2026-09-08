# GRC Auto-Arrange (`grc-autoarrange`)

**Automatic block placement and flowgraph beautifier for GNU Radio Companion (GRC)**, powered by the **Eclipse Layout Kernel (ELK)** layered Sugiyama layout engine.

---

## Features

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

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/grc-autoarrange.git
cd grc-autoarrange

# Install in editable mode or user environment
pip install --user .
```

*Prerequisite: `node` (Node.js runtime) available on PATH.*

---

## Usage

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

## License

GNU General Public License v2 or later (GPL-2.0-or-later).
