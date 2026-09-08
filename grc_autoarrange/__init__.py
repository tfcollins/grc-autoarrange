"""
grc-autoarrange: Automatic Block Layout for GNU Radio Companion using Eclipse Layout Kernel (ELK).
"""

from .elk_engine import (
    ElkEdge,
    ElkEngine,
    ElkLayoutOptions,
    ElkLayoutResult,
    ElkNode,
    ElkPort,
)
from .grc_parser import (
    dump_grc_string,
    estimate_block_dimensions,
    load_grc_file,
    save_grc_file,
)
from .gui_addon import (
    auto_arrange_flowgraph_gui,
    launch_grc,
    patch_grc,
)
from .layout_planner import (
    LayoutConfig,
    LayoutPlanner,
    snap_to_grid,
)

__version__ = "0.1.0"
__all__ = [
    "ElkEdge",
    "ElkEngine",
    "ElkLayoutOptions",
    "ElkLayoutResult",
    "ElkNode",
    "ElkPort",
    "LayoutConfig",
    "LayoutPlanner",
    "auto_arrange_flowgraph_gui",
    "dump_grc_string",
    "estimate_block_dimensions",
    "launch_grc",
    "load_grc_file",
    "patch_grc",
    "save_grc_file",
    "snap_to_grid",
]
