# Python API Reference

`grc_autoarrange` provides a Python API for programmatic flowgraph analysis, layout configuration, and formatting.

---

## `grc_autoarrange.config`

### `AutoArrangeSettings`
Handles persistent user preferences and layout defaults.

```python
from grc_autoarrange import AutoArrangeSettings

settings = AutoArrangeSettings(node_spacing=60, layer_spacing=80, direction="RIGHT")
settings.block_spacing = 72  # Convenience property setter
settings.save()  # Saves to ~/.config/gnuradio/grc_autoarrange.json
```

#### Properties & Methods
- **`block_spacing`**: Get/set general block spacing (automatically updates `node_spacing` and scales `layer_spacing`).
- **`save(file_path=None)`**: Save settings to disk.
- **`load(file_path=None)`**: Load settings from disk with fallback to defaults.

---

## `grc_autoarrange.layout_planner`

### `LayoutPlanner`
```python
from grc_autoarrange import LayoutPlanner, LayoutConfig

config = LayoutConfig(block_spacing=64)
planner = LayoutPlanner(config=config)
```

#### Methods

- **`arrange_flowgraph_data(data, selected_block_names=None, block_sizes=None)`**: Computes new (x, y) coordinates for all blocks in the flowgraph.

---

### `LayoutConfig`
Data class containing layout hyperparameters:

```python
@dataclass
class LayoutConfig:
    direction: str = "RIGHT"
    node_spacing: int = 48
    layer_spacing: int = 64
    edge_node_spacing: int = 32
    grid_size: int = 8
    margin_x: int = 16
    margin_y: int = 16
    header_gap_y: int = 32
    header_max_width: int = 1200
    header_columns: Optional[int] = None
    block_spacing: Optional[int] = None
```

---

## `grc_autoarrange.elk_engine`

### `ElkEngine`
Low-level wrapper executing the vendored ELK layout engine.

```python
from grc_autoarrange import ElkEngine, ElkNode, ElkEdge, ElkPort

engine = ElkEngine()
nodes = [ElkNode(id="src", width=160, height=80), ElkNode(id="sink", width=160, height=80)]
edges = [ElkEdge(id="e1", source="src", target="sink")]
result = engine.layout(nodes, edges)
```

---

## `grc_autoarrange.grc_parser`

### `load_grc_file(file_path: str | Path) -> dict`
Parses a `.grc` YAML file into a structured dictionary.

### `save_grc_file(data: dict, file_path: str | Path) -> None`
Serializes a flowgraph dictionary back to `.grc` YAML format on disk.

### `dump_grc_string(data: dict) -> str`
Serializes a flowgraph dictionary to a YAML string.

---

## `grc_autoarrange.gui_addon`

### `patch_grc() -> bool`
Injects the Auto-Arrange action, settings dialog, menu items, and keyboard shortcut into the active GRC GUI instance.

### `show_settings_dialog(main_window)`
Opens the interactive GTK3 configuration dialog for block spacing and layout parameters.

### `launch_grc(argv: Optional[List[str]] = None) -> int`
Patches GRC and executes GNU Radio Companion with provided arguments.
