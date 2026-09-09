# GRC Auto-Arrange

<p align="center" style="font-size: 1.25rem; font-weight: 500; color: var(--md-default-fg-color--light);">
  Intelligent, automated block placement and flowgraph beautifier for <strong>GNU Radio Companion (GRC)</strong> powered by the <strong>Eclipse Layout Kernel (ELK)</strong>.
</p>

---

## ⚡ Live Flowgraph Layout Demo

Watch messy, tangled flowgraphs automatically arrange into an optimal layered DAG with zero cable crossings:

<div class="grc-demo-container">
  <div class="grc-demo-toolbar">
    <div style="display: flex; align-items: center; gap: 10px;">
      <span id="grc-status-badge" class="grc-badge">⚠️ Messy Flowgraph (Unarranged)</span>
      <span style="opacity: 0.7; font-size: 0.75rem;">GNU Radio Companion Canvas Simulation</span>
    </div>
    <div style="display: flex; gap: 8px;">
      <button id="grc-trigger-btn" class="md-button md-button--primary" style="padding: 2px 12px; font-size: 0.75rem; border-radius: 4px; cursor: pointer;">
        ⚡ Auto-Arrange (Ctrl+Shift+A)
      </button>
    </div>
  </div>
  <div id="grc-animation-root" class="grc-demo-canvas">
    <!-- Interactive SVG rendered by flowgraph_anim.js -->
  </div>
</div>

---

## 🚀 Key Highlights

<div class="grid cards" markdown>

-   :material-view-dashboard-variant:{ .lg .middle } __Direct GRC Integration__

    ---

    Seamlessly adds **Auto Arrange Flowgraph** into GRC's Edit/Tools menu and toolbar. Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd> to tidy up your canvas in real time.

-   :material-undo-variant:{ .lg .middle } __Full Undo / Redo Support__

    ---

    Integrated directly into GRC's native state history. Hit <kbd>Ctrl</kbd> + <kbd>Z</kbd> to roll back or <kbd>Ctrl</kbd> + <kbd>Y</kbd> to redo anytime.

-   :material-format-list-group:{ .lg .middle } __Smart Block Categorization__

    ---

    Automatically isolates configuration variables (`samp_rate`, `cutoff`, etc.) into a tidy top banner while structuring signal processing blocks into a left-to-right DAG.

-   :material-grid:{ .lg .middle } __8px Grid Snapping__

    ---

    All block coordinates strictly adhere to GNU Radio Companion's standard 8-pixel alignment grid for pixel-perfect wiring.

-   :material-terminal:{ .lg .middle } __Headless CLI & Pre-Commit Hook__

    ---

    Format `.grc` flowgraph files headlessly with `grc-autoarrange -i flowgraph.grc` or automate repository linting in CI/CD pipelines.

-   :material-package-variant-closed:{ .lg .middle } __Zero NPM Dependencies__

    ---

    Includes a bundled standalone Eclipse Layout Kernel (ELK) engine that runs effortlessly on any system with Node.js installed.

</div>

---

## 📦 Quick Start

=== "1. Install"

    ```bash
    pip install --user .
    ```

=== "2. Launch GRC with Auto-Arrange"

    ```bash
    grc-autoarrange --gui my_flowgraph.grc
    ```

=== "3. Or Format Headlessly"

    ```bash
    # Format in-place
    grc-autoarrange -i my_flowgraph.grc

    # Output to new file
    grc-autoarrange input.grc -o output.grc
    ```
