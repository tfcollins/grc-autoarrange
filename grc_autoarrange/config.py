"""
Configuration Management for grc-autoarrange
Handles persistent user preferences and layout settings.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


def get_config_dir() -> Path:
    """Get the configuration directory for GNU Radio / grc-autoarrange."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base = Path(xdg_config)
    else:
        base = Path.home() / ".config"
    config_dir = base / "gnuradio"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the grc_autoarrange configuration JSON file."""
    return get_config_dir() / "grc_autoarrange.json"


@dataclass
class AutoArrangeSettings:
    node_spacing: int = 48
    layer_spacing: int = 64
    edge_node_spacing: int = 32
    direction: str = "RIGHT"  # "RIGHT", "DOWN", "LEFT", "UP"
    grid_size: int = 8
    margin_x: int = 16
    margin_y: int = 16
    header_gap_y: int = 32
    header_max_width: int = 1200
    header_columns: Optional[int] = None
    crossing_minimization: str = "LAYER_SWEEP"
    node_placement: str = "BRANDES_KOEPF"

    @property
    def block_spacing(self) -> int:
        """General block spacing shorthand (returns node_spacing)."""
        return self.node_spacing

    @block_spacing.setter
    def block_spacing(self, val: int) -> None:
        """Sets both node_spacing and proportionally scales layer_spacing."""
        self.node_spacing = max(8, int(val))
        self.layer_spacing = max(8, int(val * 1.33))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AutoArrangeSettings:
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def save(self, file_path: Optional[Path] = None) -> None:
        """Save settings to disk."""
        path = file_path or get_config_file()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            pass

    @classmethod
    def load(cls, file_path: Optional[Path] = None) -> AutoArrangeSettings:
        """Load settings from disk, falling back to defaults if not found."""
        path = file_path or get_config_file()
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return cls.from_dict(data)
            except Exception:
                pass
        return cls()
