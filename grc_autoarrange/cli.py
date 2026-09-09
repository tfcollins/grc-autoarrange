"""
Command Line Interface for grc-autoarrange
Provides CLI commands for batch formatting flowgraph files and launching GRC with the addon.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .config import AutoArrangeSettings
from .elk_engine import ElkEngine
from .grc_parser import dump_grc_string, load_grc_file, save_grc_file
from .gui_addon import launch_grc, patch_grc
from .layout_planner import LayoutConfig, LayoutPlanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grc-autoarrange",
        description="Automatically arrange GNU Radio Companion (GRC) flowgraph blocks using Eclipse Layout Kernel (ELK)."
    )

    parser.add_argument(
        "flowgraphs",
        nargs="*",
        help="Input .grc flowgraph file(s)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (for single file processing)"
    )
    parser.add_argument(
        "-i", "--in-place",
        action="store_true",
        help="Overwrite input .grc files in place"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GNU Radio Companion with the Auto-Arrange addon enabled"
    )
    parser.add_argument(
        "-d", "--direction",
        choices=["RIGHT", "DOWN", "LEFT", "UP"],
        default=None,
        help="Layout flow direction (default: from settings or RIGHT)"
    )
    parser.add_argument(
        "-s", "--spacing", "--block-spacing",
        type=int,
        dest="block_spacing",
        default=None,
        help="Set general block spacing in pixels (scales node and layer spacing proportionally)"
    )
    parser.add_argument(
        "--node-spacing",
        type=int,
        default=None,
        help="Spacing between adjacent nodes in the same layer in pixels (default: 48)"
    )
    parser.add_argument(
        "--layer-spacing",
        type=int,
        default=None,
        help="Spacing between consecutive layers in pixels (default: 64)"
    )
    parser.add_argument(
        "--header-columns",
        type=int,
        default=None,
        help="Max columns in the top header/variable banner"
    )
    parser.add_argument(
        "--save-defaults",
        action="store_true",
        help="Save the specified spacing and layout options as persistent user defaults"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform layout calculation without modifying files on disk"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose diagnostic logging"
    )

    return parser


def arrange_file(
    input_file: str | Path,
    output_file: Optional[str | Path] = None,
    config: Optional[LayoutConfig] = None,
    in_place: bool = False,
    dry_run: bool = False,
    verbose: bool = False
) -> bool:
    """Format and arrange a single .grc flowgraph file."""
    in_path = Path(input_file)
    if not in_path.exists():
        print(f"Error: File not found: {in_path}", file=sys.stderr)
        return False

    if verbose:
        print(f"Loading {in_path}...")

    data = load_grc_file(in_path)
    planner = LayoutPlanner(config=config)
    coords = planner.arrange_flowgraph_data(data)

    if verbose:
        print(f"Arranged {len(coords)} blocks.")

    # Apply coordinates
    if "options" in coords and "options" in data:
        data["options"].setdefault("states", {})["coordinate"] = list(coords["options"])

    for block in data.get("blocks", []):
        bname = block.get("name")
        if bname in coords:
            block.setdefault("states", {})["coordinate"] = list(coords[bname])

    if dry_run:
        print(f"[Dry Run] Successfully computed layout for {in_path}")
        return True

    target_path = in_path if in_place else Path(output_file) if output_file else None
    if target_path:
        save_grc_file(data, target_path)
        if verbose:
            print(f"Saved arranged flowgraph to {target_path}")
    else:
        # Print to stdout
        sys.stdout.write(dump_grc_string(data))

    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui:
        # Forward arguments to GRC
        grc_args = ["gnuradio-companion"] + args.flowgraphs
        return launch_grc(grc_args)

    # Load persistent user defaults
    settings = AutoArrangeSettings.load()

    if args.block_spacing is not None:
        settings.block_spacing = args.block_spacing
    if args.node_spacing is not None:
        settings.node_spacing = args.node_spacing
    if args.layer_spacing is not None:
        settings.layer_spacing = args.layer_spacing
    if args.direction is not None:
        settings.direction = args.direction
    if args.header_columns is not None:
        settings.header_columns = args.header_columns

    if args.save_defaults:
        settings.save()
        print(f"Persistent layout defaults saved: node_spacing={settings.node_spacing}, layer_spacing={settings.layer_spacing}, direction={settings.direction}")
        if not args.flowgraphs:
            return 0

    if not args.flowgraphs:
        parser.print_help()
        return 0

    config = LayoutConfig.from_settings(settings)

    if len(args.flowgraphs) > 1 and args.output and not args.in_place:
        print("Error: -o/--output cannot be used with multiple input files unless --in-place is set.", file=sys.stderr)
        return 1

    success_all = True
    for fg_path in args.flowgraphs:
        out_path = args.output if len(args.flowgraphs) == 1 else None
        res = arrange_file(
            input_file=fg_path,
            output_file=out_path,
            config=config,
            in_place=args.in_place,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        if not res:
            success_all = False

    return 0 if success_all else 1


if __name__ == "__main__":
    sys.exit(main())
