"""
Layout Planner for GNU Radio Companion Flowgraphs
Orchestrates block categorization, ELK graph generation, header grid placement, and grid snapping.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from .config import AutoArrangeSettings
from .elk_engine import ElkEdge, ElkEngine, ElkLayoutOptions, ElkNode, ElkPort
from .grc_parser import HEADER_BLOCK_IDS, estimate_block_dimensions


def snap_to_grid(value: float, grid_size: int = 8) -> int:
    """Snap a coordinate value to the nearest GRC grid point."""
    return int(round(value / grid_size) * grid_size)


@dataclass
class LayoutConfig:
    direction: str = "RIGHT"  # "RIGHT", "DOWN", "LEFT", "UP"
    node_spacing: int = 48
    layer_spacing: int = 64
    edge_node_spacing: int = 32
    grid_size: int = 8
    margin_x: int = 16
    margin_y: int = 16
    header_gap_y: int = 32
    header_max_width: int = 1200
    header_columns: Optional[int] = None
    crossing_minimization: str = "LAYER_SWEEP"
    node_placement: str = "BRANDES_KOEPF"
    block_spacing: Optional[int] = None

    def __post_init__(self):
        if self.block_spacing is not None:
            self.node_spacing = max(8, int(self.block_spacing))
            self.layer_spacing = max(8, int(self.block_spacing * 1.33))

    @classmethod
    def from_settings(cls, settings: AutoArrangeSettings) -> LayoutConfig:
        return cls(
            direction=settings.direction,
            node_spacing=settings.node_spacing,
            layer_spacing=settings.layer_spacing,
            edge_node_spacing=settings.edge_node_spacing,
            grid_size=settings.grid_size,
            margin_x=settings.margin_x,
            margin_y=settings.margin_y,
            header_gap_y=settings.header_gap_y,
            header_max_width=settings.header_max_width,
            header_columns=settings.header_columns,
            crossing_minimization=settings.crossing_minimization,
            node_placement=settings.node_placement,
        )


class LayoutPlanner:
    """Computes automated layout coordinates for GRC flowgraphs using ELK."""

    def __init__(
        self,
        engine: Optional[ElkEngine] = None,
        config: Optional[LayoutConfig] = None
    ):
        self.engine = engine or ElkEngine()
        self.config = config or LayoutConfig()

    def arrange_flowgraph_data(
        self,
        data: Dict[str, Any],
        selected_block_names: Optional[Set[str]] = None,
        block_sizes: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> Dict[str, Tuple[int, int]]:
        """
        Calculates new (x, y) coordinates for blocks in the GRC flowgraph data dict.

        Args:
            data: Parsed .grc dictionary containing 'options', 'blocks', 'connections'.
            selected_block_names: If provided, only rearrange these selected blocks.
            block_sizes: Optional mapping of block_name -> (width, height) (e.g. from GRC GUI canvas).

        Returns:
            Dictionary mapping block name -> (x, y) integer coordinate.
        """
        options = data.get("options", {})
        blocks = data.get("blocks", [])
        connections = data.get("connections", [])

        # Collect port counts and connections
        sink_ports: Dict[str, Set[str]] = {}
        source_ports: Dict[str, Set[str]] = {}
        valid_edges: List[ElkEdge] = []

        for idx, conn in enumerate(connections):
            if not isinstance(conn, (list, tuple)) or len(conn) < 4:
                continue
            src, src_port, sink, sink_port = str(conn[0]), str(conn[1]), str(conn[2]), str(conn[3])
            
            source_ports.setdefault(src, set()).add(src_port)
            sink_ports.setdefault(sink, set()).add(sink_port)

            if selected_block_names is None or (src in selected_block_names and sink in selected_block_names):
                valid_edges.append(
                    ElkEdge(
                        id=f"e_{idx}_{src}_{sink}",
                        source=src,
                        target=sink,
                        source_port=src_port,
                        target_port=sink_port
                    )
                )

        # Classify blocks
        header_blocks: List[Dict[str, Any]] = []
        signal_blocks: List[Dict[str, Any]] = []
        floating_blocks: List[Dict[str, Any]] = []

        for b in blocks:
            name = b.get("name")
            bid = b.get("id", "")
            if not name:
                continue

            if selected_block_names is not None and name not in selected_block_names:
                continue

            has_connections = (name in source_ports) or (name in sink_ports)

            if bid in HEADER_BLOCK_IDS and not has_connections:
                header_blocks.append(b)
            elif has_connections:
                signal_blocks.append(b)
            else:
                floating_blocks.append(b)

        # Determine sizes
        sizes: Dict[str, Tuple[float, float]] = {}
        if block_sizes:
            sizes.update(block_sizes)

        # Estimate missing sizes
        if options and "options" not in sizes:
            sizes["options"] = (160.0, 80.0)

        for b in blocks:
            name = b.get("name")
            if name and name not in sizes:
                sinks_cnt = len(sink_ports.get(name, []))
                srcs_cnt = len(source_ports.get(name, []))
                sizes[name] = estimate_block_dimensions(b, sinks_cnt, srcs_cnt)

        new_coordinates: Dict[str, Tuple[int, int]] = {}

        # Handle Selection-Only mode
        if selected_block_names is not None:
            return self._arrange_selected_subgraph(
                signal_blocks + header_blocks + floating_blocks,
                valid_edges,
                sizes,
                sink_ports,
                source_ports
            )

        # 1. Arrange options block
        opt_x = snap_to_grid(self.config.margin_x, self.config.grid_size)
        opt_y = snap_to_grid(self.config.margin_y, self.config.grid_size)
        new_coordinates["options"] = (opt_x, opt_y)
        opt_w, opt_h = sizes.get("options", (160.0, 80.0))

        # 2. Arrange Header Blocks in top grid
        curr_x = opt_x + snap_to_grid(opt_w + self.config.node_spacing, self.config.grid_size)
        curr_y = opt_y
        row_max_h = opt_h
        max_header_y = opt_y + opt_h

        # Sort header blocks nicely: variables first, imports next, etc.
        header_blocks.sort(key=lambda b: (b.get("id") != "import", b.get("id") != "variable", b.get("name", "")))

        col_idx = 0
        max_cols = self.config.header_columns

        for hb in header_blocks:
            hname = hb.get("name")
            hw, hh = sizes.get(hname, (160.0, 64.0))

            # Check for line wrap
            if (max_cols and col_idx >= max_cols) or (not max_cols and curr_x + hw > self.config.header_max_width):
                curr_x = opt_x
                curr_y += snap_to_grid(row_max_h + 16, self.config.grid_size)
                row_max_h = hh
                col_idx = 0

            new_coordinates[hname] = (snap_to_grid(curr_x, self.config.grid_size), snap_to_grid(curr_y, self.config.grid_size))
            curr_x += snap_to_grid(hw + 16, self.config.grid_size)
            row_max_h = max(row_max_h, hh)
            max_header_y = max(max_header_y, curr_y + hh)
            col_idx += 1

        dag_start_y = snap_to_grid(max_header_y + self.config.header_gap_y, self.config.grid_size)

        # 3. Build ELK nodes for Signal Processing Graph
        elk_nodes: List[ElkNode] = []
        for sb in signal_blocks:
            sname = sb.get("name")
            sw, sh = sizes.get(sname, (160.0, 80.0))
            ports: List[ElkPort] = []

            # Add sorted sink ports
            sinks = sorted(list(sink_ports.get(sname, set())))
            for p_idx, p_id in enumerate(sinks):
                ports.append(ElkPort(id=p_id, side="WEST", index=p_idx, x=-8.0, y=20.0 + p_idx * 28.0))

            # Add sorted source ports
            srcs = sorted(list(source_ports.get(sname, set())))
            for p_idx, p_id in enumerate(srcs):
                ports.append(ElkPort(id=p_id, side="EAST", index=p_idx, x=sw, y=20.0 + p_idx * 28.0))

            elk_nodes.append(ElkNode(id=sname, width=sw, height=sh, ports=ports))

        # Run ELK layout
        dag_height = 0.0
        if elk_nodes:
            elk_opts = ElkLayoutOptions(
                direction=self.config.direction,
                spacing_node_node=self.config.node_spacing,
                spacing_node_node_between_layers=self.config.layer_spacing,
                spacing_edge_node_between_layers=self.config.edge_node_spacing,
                crossing_minimization=self.config.crossing_minimization,
                node_placement=self.config.node_placement,
            )
            result = self.engine.layout(elk_nodes, valid_edges, elk_opts)
            dag_height = result.height

            for sname, (nx, ny) in result.node_positions.items():
                final_x = snap_to_grid(nx + self.config.margin_x, self.config.grid_size)
                final_y = snap_to_grid(ny + dag_start_y, self.config.grid_size)
                new_coordinates[sname] = (final_x, final_y)

        # 4. Arrange Floating / Disconnected blocks
        if floating_blocks:
            float_start_y = snap_to_grid(dag_start_y + dag_height + self.config.header_gap_y, self.config.grid_size)
            fx = snap_to_grid(self.config.margin_x, self.config.grid_size)
            fy = float_start_y
            row_h = 0.0
            for fb in floating_blocks:
                fname = fb.get("name")
                fw, fh = sizes.get(fname, (160.0, 80.0))
                if fx + fw > self.config.header_max_width:
                    fx = snap_to_grid(self.config.margin_x, self.config.grid_size)
                    fy += snap_to_grid(row_h + 16, self.config.grid_size)
                    row_h = fh

                new_coordinates[fname] = (snap_to_grid(fx, self.config.grid_size), snap_to_grid(fy, self.config.grid_size))
                fx += snap_to_grid(fw + 16, self.config.grid_size)
                row_h = max(row_h, fh)

        return new_coordinates

    def _arrange_selected_subgraph(
        self,
        blocks: List[Dict[str, Any]],
        edges: List[ElkEdge],
        sizes: Dict[str, Tuple[float, float]],
        sink_ports: Dict[str, Set[str]],
        source_ports: Dict[str, Set[str]]
    ) -> Dict[str, Tuple[int, int]]:
        """Arranges only a subset of selected blocks around their current bounding center."""
        if not blocks:
            return {}

        orig_coords = [
            b.get("states", {}).get("coordinate", [0, 0])
            for b in blocks
            if isinstance(b.get("states", {}).get("coordinate"), (list, tuple))
        ]
        if orig_coords:
            min_x = min(c[0] for c in orig_coords)
            min_y = min(c[1] for c in orig_coords)
        else:
            min_x, min_y = 100, 100

        elk_nodes: List[ElkNode] = []
        for b in blocks:
            name = b.get("name")
            bw, bh = sizes.get(name, (160.0, 80.0))
            ports: List[ElkPort] = []
            for p_idx, p_id in enumerate(sorted(list(sink_ports.get(name, set())))):
                ports.append(ElkPort(id=p_id, side="WEST", index=p_idx, x=-8.0, y=20.0 + p_idx * 28.0))
            for p_idx, p_id in enumerate(sorted(list(source_ports.get(name, set())))):
                ports.append(ElkPort(id=p_id, side="EAST", index=p_idx, x=bw, y=20.0 + p_idx * 28.0))
            elk_nodes.append(ElkNode(id=name, width=bw, height=bh, ports=ports))

        elk_opts = ElkLayoutOptions(
            direction=self.config.direction,
            spacing_node_node=self.config.node_spacing,
            spacing_node_node_between_layers=self.config.layer_spacing,
            spacing_edge_node_between_layers=self.config.edge_node_spacing,
        )
        result = self.engine.layout(elk_nodes, edges, elk_opts)

        coords: Dict[str, Tuple[int, int]] = {}
        for name, (nx, ny) in result.node_positions.items():
            coords[name] = (
                snap_to_grid(nx + min_x, self.config.grid_size),
                snap_to_grid(ny + min_y, self.config.grid_size)
            )
        return coords
