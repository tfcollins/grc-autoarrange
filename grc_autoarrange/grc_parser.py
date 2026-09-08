"""
GRC Flowgraph Parser and Serializer
Handles reading and writing GNU Radio Companion .grc (YAML) files and estimating block sizes.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


# Block types that are typically non-signal configuration / header elements
HEADER_BLOCK_IDS = {
    "options",
    "variable",
    "variable_qtgui_range",
    "variable_qtgui_chooser",
    "variable_qtgui_check_box",
    "variable_qtgui_push_button",
    "variable_qtgui_entry",
    "variable_qtgui_label",
    "variable_config",
    "variable_struct",
    "variable_function_probe",
    "variable_tag_object",
    "import",
    "parameter",
    "snippet",
    "epy_module",
}


def load_grc_file(file_path: str | Path) -> Dict[str, Any]:
    """Load a GRC YAML flowgraph from disk."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"GRC file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid GRC file format in {path}: expected YAML mapping")

    return data


def dump_grc_string(data: Dict[str, Any]) -> str:
    """Serialize GRC flowgraph data to YAML string."""
    return yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120
    )


def save_grc_file(data: Dict[str, Any], file_path: str | Path) -> None:
    """Save GRC flowgraph data to a .grc file on disk."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = dump_grc_string(data)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def estimate_block_dimensions(
    block: Dict[str, Any],
    sink_count: int = 0,
    source_count: int = 0
) -> Tuple[int, int]:
    """
    Estimate block width and height for offline/headless layout computation.
    Matches standard GNU Radio Companion canvas sizing heuristics.
    """
    block_id = block.get("id", "")
    name = block.get("name", "")
    params = block.get("parameters", {}) or {}

    if block_id == "options":
        return (160, 80)
    elif block_id == "note":
        comment = params.get("note", "") or ""
        lines = max(1, len(str(comment).splitlines()))
        return (max(160, min(360, len(str(comment)) * 8)), max(60, lines * 20 + 30))
    elif block_id == "variable":
        val_str = str(params.get("value", ""))
        width = max(160, min(320, 40 + max(len(name), len(val_str)) * 9))
        return (width, 64)
    elif block_id.startswith("variable_"):
        return (200, 80)
    elif block_id == "import":
        return (160, 60)
    elif block_id == "parameter":
        return (180, 72)
    elif block_id == "snippet":
        return (180, 80)

    # Signal processing block
    max_ports = max(sink_count, source_count, 1)
    port_height = max_ports * 28 + 24

    param_count = sum(
        1 for k, v in params.items()
        if k not in ("affinity", "alias", "comment", "hide") and v not in ("", None)
    )
    param_height = min(120, param_count * 18 + 20)
    height = max(64, port_height, param_height)

    # Estimate width from name and parameter labels
    text_lengths = [len(name), len(block_id)] + [len(str(v)[:20]) for v in params.values() if v is not None]
    max_text_len = max(text_lengths) if text_lengths else 10
    width = max(160, min(320, 50 + max_text_len * 8))

    return (width, height)
