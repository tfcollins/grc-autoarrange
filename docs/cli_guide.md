# CLI & Batch Formatter Guide

`grc-autoarrange` includes a standalone command-line interface for formatting `.grc` flowgraphs without launching the GUI.

---

## Command Syntax

```bash
grc-autoarrange [OPTIONS] flowgraph.grc [flowgraph2.grc ...]
```

### Options Reference

| Flag | Description | Default |
| :--- | :--- | :--- |
| `-i`, `--in-place` | Overwrite input flowgraph files directly on disk. | `False` |
| `-o`, `--output` | Write output to a specified `.grc` file path. | `stdout` |
| `-s`, `--spacing`, `--block-spacing` | Set general block spacing (scales node & layer spacing). | `None` (from config) |
| `--node-spacing` | Spacing between nodes in the same layer (pixels). | `48` |
| `--layer-spacing` | Spacing between consecutive layers (pixels). | `64` |
| `-d`, `--direction` | Flow direction: `RIGHT`, `DOWN`, `LEFT`, `UP`. | `RIGHT` |
| `--header-columns` | Max number of columns in the header variable grid. | `None` (auto-wrap) |
| `--save-defaults` | Save specified spacing and direction as persistent user defaults. | `False` |
| `--gui` | Launch GNU Radio Companion with the Auto-Arrange addon. | `False` |
| `--dry-run` | Calculate layout without modifying files. | `False` |
| `-v`, `--verbose` | Print detailed step-by-step layout logging. | `False` |

---

## Examples

### 1. In-Place Formatting with Custom Spacing
Format a flowgraph file directly with custom block spacing:
```bash
grc-autoarrange -i my_receiver.grc --spacing 60
```

### 2. Output to a New File
Format and save as a separate copy:
```bash
grc-autoarrange messy.grc -o clean.grc
```

### 3. Save Default Spacing Preferences
Save your preferred block spacing persistently so all future GUI and CLI formatting runs use it automatically:
```bash
grc-autoarrange --spacing 72 --save-defaults
```

### 4. Custom Spacing & Vertical Flow
Arrange with top-to-bottom layout and larger spacing:
```bash
grc-autoarrange input.grc -o output.grc --direction DOWN --node-spacing 80 --layer-spacing 100
```

### 5. Dry Run & Verification
Verify layout calculations without writing changes:
```bash
grc-autoarrange --dry-run my_flowgraph.grc
```

---

## Pre-Commit Hook Integration

You can easily add `grc-autoarrange` to your `.pre-commit-config.yaml` to ensure all GNU Radio flowgraphs in your repository remain formatted:

```yaml
repos:
  - repo: local
    hooks:
      - id: grc-autoarrange
        name: Auto-arrange GNU Radio Flowgraphs
        entry: grc-autoarrange -i --spacing 48
        language: python
        types: [yaml]
        files: \.grc$
```
