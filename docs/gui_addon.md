# GNU Radio Companion GUI Addon

`grc-autoarrange` includes native GUI hooks for **GNU Radio Companion (GRC)**. It adds menu options, a toolbar button, keyboard shortcuts, and full undo/redo integration directly within GRC's GTK3 canvas.

---

## Visual Comparison

<div class="grid cards" markdown>

-   __Before Auto-Arrange__

    ---

    ![Before Auto-Arrange](assets/grc_window_before.png)
    *Messy layout with backwards routing and overlapping wires.*

-   __After Auto-Arrange (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd>)__

    ---

    ![After Auto-Arrange](assets/grc_window_after.png)
    *Layered Sugiyama DAG with top variable header and 8px grid alignment.*

</div>

---

## Launching GRC with Auto-Arrange

To launch GNU Radio Companion with the Auto-Arrange addon enabled:

```bash
grc-autoarrange --gui [flowgraph.grc]
```

---

## Keyboard Shortcuts & Controls

| Action | Shortcut / Access | Description |
| :--- | :--- | :--- |
| **Auto-Arrange Flowgraph** | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd> | Automatically arranges all blocks (or selected blocks). |
| **Menu Access (Edit)** | `Edit` &rarr; `Auto Arrange Flowgraph` | Triggers layout calculation and redraws canvas. |
| **Menu Access (Tools)** | `Tools` &rarr; `Auto Arrange Flowgraph` | Alternative menu placement. |
| **Toolbar Button** | :material-format-justify-fill: icon on toolbar | Single-click auto-arrange. |
| **Undo** | <kbd>Ctrl</kbd> + <kbd>Z</kbd> | Reverts canvas to state prior to auto-arrange. |
| **Redo** | <kbd>Ctrl</kbd> + <kbd>Y</kbd> / <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Z</kbd> | Re-applies auto-arrange layout. |

---

## Selection-Only Layout

If your flowgraph is large and you only want to organize a localized portion (e.g. a demodulator subsystem):

1. **Select the blocks** you want to organize by dragging a selection rectangle or holding <kbd>Ctrl</kbd> and clicking.
2. Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd>.
3. Only the selected blocks will be arranged relative to each other; all unselected blocks remain untouched!

---

## How GUI Layout Works

1. **Visual Measurement**: The addon queries PangoCairo for the exact rendered dimensions (`width` and `height`) of each block on canvas.
2. **Graph Model**: Connections and port offsets are extracted from the active flowgraph instance.
3. **ELK Execution**: The layout is computed in milliseconds using ELK's Layered algorithm.
4. **Canvas Update**: New coordinates are assigned, the canvas is redrawn, and an undo checkpoint is registered with `page.state_cache`.
