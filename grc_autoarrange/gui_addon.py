"""
GNU Radio Companion GUI Addon Integration
Hooks into GRC's GTK3 GUI application to add Auto-Arrange action, menu entries, toolbar button, and shortcut.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, List, Optional, Set

from .elk_engine import ElkEngine
from .layout_planner import LayoutConfig, LayoutPlanner

log = logging.getLogger(__name__)

ACTION_NAME = "flow_graph_auto_arrange"
_PATCHED = False


def auto_arrange_flowgraph_gui(
    flow_graph: Any,
    main_window: Any,
    page: Any,
    config: Optional[LayoutConfig] = None
) -> bool:
    """
    Executes auto-arrange on a live GRC GUI FlowGraph instance.
    Updates block coordinates, refreshes the canvas, and records an undo checkpoint.
    """
    try:
        # Check if user selected multiple blocks for localized arrangement
        selected_blocks = list(flow_graph.selected_blocks())
        selected_names: Optional[Set[str]] = None
        if len(selected_blocks) > 1:
            selected_names = {b.name for b in selected_blocks if getattr(b, "name", None)}

        # Capture live PangoCairo visual dimensions from canvas
        block_sizes = {}
        for b in flow_graph.blocks:
            bname = getattr(b, "name", None) or getattr(b, "identifier", None)
            if bname:
                w = getattr(b, "width", 160.0) or 160.0
                h = getattr(b, "height", 80.0) or 80.0
                block_sizes[bname] = (float(w), float(h))

        # Also get options block dimensions
        if hasattr(flow_graph, "options_block") and flow_graph.options_block:
            opt_b = flow_graph.options_block
            block_sizes["options"] = (
                float(getattr(opt_b, "width", 160.0) or 160.0),
                float(getattr(opt_b, "height", 80.0) or 80.0)
            )

        planner = LayoutPlanner(config=config)
        export_dict = flow_graph.export_data()
        new_coords = planner.arrange_flowgraph_data(
            export_dict,
            selected_block_names=selected_names,
            block_sizes=block_sizes
        )

        if not new_coords:
            return False

        # Apply coordinates to live canvas blocks
        for b in flow_graph.blocks:
            bname = getattr(b, "name", None) or getattr(b, "identifier", None)
            if bname and bname in new_coords:
                b.coordinate = new_coords[bname]

        if "options" in new_coords and hasattr(flow_graph, "options_block") and flow_graph.options_block:
            flow_graph.options_block.coordinate = new_coords["options"]

        # Update GUI elements
        if hasattr(main_window, "vars") and main_window.vars:
            main_window.vars.update_gui(flow_graph.blocks)

        flow_graph.update()

        if hasattr(page, "drawing_area") and page.drawing_area:
            page.drawing_area.queue_draw()

        # Save to undo/redo state cache
        if hasattr(page, "state_cache") and page.state_cache:
            page.state_cache.save_new_state(flow_graph.export_data())
            page.saved = False

        return True

    except Exception as exc:
        log.exception("Failed to auto-arrange flowgraph: %s", exc)
        if hasattr(main_window, "add_console_line"):
            main_window.add_console_line(f"Auto-Arrange error: {exc}\n")
        return False


def patch_grc() -> bool:
    """
    Patches gnuradio.grc.gui modules to inject the Auto Arrange action, menu items,
    toolbar button, and shortcut.
    """
    global _PATCHED
    if _PATCHED:
        return True

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("PangoCairo", "1.0")

        # Import Platform first to avoid GRC circular import quirks
        from gnuradio.grc.gui.Platform import Platform
        from gnuradio.grc.gui.Application import Application
        from gnuradio.grc.gui import Actions, Bars

        full_action_name = f"app.{ACTION_NAME}"

        # 1. Register Action in Actions namespace
        if full_action_name not in Actions.get_actions():
            auto_arrange_action = Actions.actions.register(
                name=full_action_name,
                label="_Auto Arrange Flowgraph",
                tooltip="Automatically arrange flowgraph blocks using Eclipse Layout Kernel (ELK)",
                icon_name="format-justify-fill",
                keypresses=["<Primary><Shift>A"],
            )
        else:
            auto_arrange_action = Actions.actions[full_action_name]

        setattr(Actions, "FLOW_GRAPH_AUTO_ARRANGE", auto_arrange_action)

        # 2. Add to Menu Bar: in _Edit menu (after alignment options) and in _Tools menu
        edit_menu = None
        tools_menu = None
        for item in Bars.MENU_BAR_LIST:
            if isinstance(item, tuple) and len(item) == 2:
                if item[0] == "_Edit":
                    edit_menu = item[1]
                elif item[0] == "_Tools":
                    tools_menu = item[1]

        if edit_menu is not None:
            found = any(
                auto_arrange_action in group if isinstance(group, list) else False
                for group in edit_menu
            )
            if not found:
                edit_menu.append([auto_arrange_action])

        if tools_menu is not None:
            found = any(
                auto_arrange_action in group if isinstance(group, list) else False
                for group in tools_menu
            )
            if not found:
                tools_menu.append([auto_arrange_action])

        # 3. Add to Toolbar (in edit section)
        toolbar_found = any(
            auto_arrange_action in group if isinstance(group, list) else False
            for group in Bars.TOOLBAR_LIST
        )
        if not toolbar_found:
            # Add near undo/redo or block manipulation
            Bars.TOOLBAR_LIST.insert(5, [auto_arrange_action])

        # 4. Patch Application._handle_action
        orig_handle_action = Application._handle_action

        def patched_handle_action(self, action, *args):
            if action == auto_arrange_action or action == getattr(Actions, "FLOW_GRAPH_AUTO_ARRANGE", None):
                main = self.main_window
                page = main.current_page
                flow_graph = page.flow_graph if page else None
                if flow_graph:
                    auto_arrange_flowgraph_gui(flow_graph, main, page)
                return

            return orig_handle_action(self, action, *args)

        Application._handle_action = patched_handle_action

        _PATCHED = True
        log.info("Successfully patched GNU Radio Companion with Auto-Arrange addon.")
        return True

    except Exception as exc:
        log.warning("Could not patch GNU Radio Companion GUI: %s", exc)
        return False


def launch_grc(argv: Optional[List[str]] = None) -> int:
    """Launch GNU Radio Companion with the Auto-Arrange addon enabled."""
    patch_grc()
    from gnuradio.grc.main import main
    old_argv = sys.argv
    try:
        if argv is not None:
            sys.argv = argv
        return main() or 0
    finally:
        sys.argv = old_argv
