"""
ELK Layout Engine Bridge
Translates graph elements to ELK JSON format and invokes the vendored ELK engine.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ElkPort:
    id: str
    side: str = "EAST"  # "WEST", "EAST", "NORTH", "SOUTH"
    index: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: float = 8.0
    height: float = 8.0

    def to_dict(self, port_global_id: str) -> Dict[str, Any]:
        layout_opts: Dict[str, str] = {
            "elk.port.side": self.side
        }
        if self.index is not None:
            layout_opts["elk.port.index"] = str(self.index)

        d: Dict[str, Any] = {
            "id": port_global_id,
            "width": self.width,
            "height": self.height,
            "layoutOptions": layout_opts
        }
        if self.x is not None:
            d["x"] = self.x
        if self.y is not None:
            d["y"] = self.y
        return d


@dataclass
class ElkNode:
    id: str
    width: float = 160.0
    height: float = 80.0
    ports: List[ElkPort] = field(default_factory=list)
    layout_options: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "width": max(10.0, float(self.width)),
            "height": max(10.0, float(self.height)),
        }
        layout_opts = dict(self.layout_options)
        if self.ports:
            has_pos = any(p.x is not None or p.y is not None for p in self.ports)
            layout_opts.setdefault("elk.portConstraints", "FIXED_POS" if has_pos else "FIXED_ORDER")
            d["ports"] = [
                p.to_dict(port_global_id=f"{self.id}__p__{p.id}")
                for p in self.ports
            ]
        if layout_opts:
            d["layoutOptions"] = layout_opts
        return d


@dataclass
class ElkEdge:
    id: str
    source: str
    target: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        src_endpoint = f"{self.source}__p__{self.source_port}" if self.source_port else self.source
        tgt_endpoint = f"{self.target}__p__{self.target_port}" if self.target_port else self.target
        return {
            "id": self.id,
            "sources": [src_endpoint],
            "targets": [tgt_endpoint],
        }


@dataclass
class ElkLayoutOptions:
    algorithm: str = "layered"
    direction: str = "RIGHT"
    spacing_node_node: int = 48
    spacing_node_node_between_layers: int = 64
    spacing_edge_node_between_layers: int = 32
    crossing_minimization: str = "LAYER_SWEEP"
    node_placement: str = "BRANDES_KOEPF"
    alignment: str = "CENTER"
    separate_connected_components: bool = True

    def to_dict(self) -> Dict[str, str]:
        return {
            "elk.algorithm": self.algorithm,
            "elk.direction": self.direction,
            "elk.spacing.nodeNode": str(self.spacing_node_node),
            "elk.layered.spacing.nodeNodeBetweenLayers": str(self.spacing_node_node_between_layers),
            "elk.layered.spacing.edgeNodeBetweenLayers": str(self.spacing_edge_node_between_layers),
            "elk.layered.crossingMinimization.strategy": self.crossing_minimization,
            "elk.layered.nodePlacement.strategy": self.node_placement,
            "elk.alignment": self.alignment,
            "elk.separateConnectedComponents": "true" if self.separate_connected_components else "false",
            "elk.padding": "[top=0,left=0,bottom=0,right=0]",
        }


@dataclass
class ElkLayoutResult:
    node_positions: Dict[str, Tuple[float, float]]  # node_id -> (x, y)
    width: float
    height: float
    raw: Dict[str, Any]


class ElkEngine:
    """Executes ELK layout using the vendored standalone ELK JS bundle."""

    def __init__(self, node_binary: Optional[str] = None):
        self.node_binary = node_binary or shutil.which("node") or shutil.which("nodejs")
        self.vendor_dir = Path(__file__).parent / "vendor"
        self.runner_script = self.vendor_dir / "elk_runner.js"
        self.bundle_file = self.vendor_dir / "elk.bundled.js"

        if not self.bundle_file.exists():
            raise FileNotFoundError(f"ELK bundle not found at {self.bundle_file}")

    def layout(
        self,
        nodes: List[ElkNode],
        edges: List[ElkEdge],
        options: Optional[ElkLayoutOptions] = None
    ) -> ElkLayoutResult:
        """Run ELK layout for given nodes and edges."""
        if not self.node_binary:
            raise RuntimeError(
                "Node.js runtime not found on PATH. Please install Node.js (e.g. sudo apt install nodejs) "
                "to use the ELK layout engine."
            )

        opts = options or ElkLayoutOptions()

        graph_dict = {
            "id": "root",
            "layoutOptions": opts.to_dict(),
            "children": [n.to_dict() for n in nodes],
            "edges": [e.to_dict() for e in edges]
        }

        input_json = json.dumps(graph_dict)

        proc = subprocess.Popen(
            [self.node_binary, str(self.runner_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = proc.communicate(input=input_json)

        if proc.returncode != 0:
            raise RuntimeError(f"ELK layout execution failed (code {proc.returncode}): {stderr.strip()}")

        try:
            result = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to decode ELK JSON output: {exc}\nRaw output: {stdout}") from exc

        positions: Dict[str, Tuple[float, float]] = {}
        for child in result.get("children", []):
            cid = child.get("id")
            cx = float(child.get("x", 0.0))
            cy = float(child.get("y", 0.0))
            if cid:
                positions[cid] = (cx, cy)

        total_width = float(result.get("width", 0.0))
        total_height = float(result.get("height", 0.0))

        return ElkLayoutResult(
            node_positions=positions,
            width=total_width,
            height=total_height,
            raw=result
        )
