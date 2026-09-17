"""
GNU Radio Companion GUI Addon Integration
Hooks into GRC's GTK3 GUI application to add Auto-Arrange action, settings dialog, menu entries, toolbar button, and shortcut.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, List, Optional, Set

from .config import AutoArrangeSettings
from .elk_engine import ElkEngine
from .layout_planner import LayoutConfig, LayoutPlanner

log = logging.getLogger(__name__)

ACTION_NAME = "flow_graph_auto_arrange"
SETTINGS_ACTION_NAME = "flow_graph_auto_arrange_settings"
_PATCHED = False

# Set on the re-executed child so a broken GNU Radio install cannot cause an exec loop.
NO_REEXEC_ENV = "GRC_AUTOARRANGE_NO_REEXEC"


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
        # Load user-configured settings if custom config not passed
        if config is None:
            settings = AutoArrangeSettings.load()
            config = LayoutConfig.from_settings(settings)

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


def show_settings_dialog(main_window: Any) -> None:
    """Displays the GTK3 Auto-Arrange Settings Dialog."""
    try:
        from gi.repository import Gtk

        settings = AutoArrangeSettings.load()

        dialog = Gtk.Dialog(
            title="Auto-Arrange Layout Settings",
            parent=main_window,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        dialog.set_default_size(380, 320)

        content = dialog.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(20)
        content.set_margin_end(20)

        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(12)
        content.add(grid)

        # 1. Node Spacing (Vertical in RIGHT flow)
        lbl_node = Gtk.Label(label="Block Spacing (Vertical):", xalign=0)
        spin_node = Gtk.SpinButton.new_with_range(8, 300, 8)
        spin_node.set_value(settings.node_spacing)
        grid.attach(lbl_node, 0, 0, 1, 1)
        grid.attach(spin_node, 1, 0, 1, 1)

        # 2. Layer Spacing (Horizontal in RIGHT flow)
        lbl_layer = Gtk.Label(label="Layer Spacing (Horizontal):", xalign=0)
        spin_layer = Gtk.SpinButton.new_with_range(8, 400, 8)
        spin_layer.set_value(settings.layer_spacing)
        grid.attach(lbl_layer, 0, 1, 1, 1)
        grid.attach(spin_layer, 1, 1, 1, 1)

        # 3. Flow Direction
        lbl_dir = Gtk.Label(label="Flow Direction:", xalign=0)
        combo_dir = Gtk.ComboBoxText()
        directions = ["RIGHT", "DOWN", "LEFT", "UP"]
        for d in directions:
            combo_dir.append_text(d)
        combo_dir.set_active(directions.index(settings.direction) if settings.direction in directions else 0)
        grid.attach(lbl_dir, 0, 2, 1, 1)
        grid.attach(combo_dir, 1, 2, 1, 1)

        # 4. Header Columns
        lbl_hdr = Gtk.Label(label="Header Columns (0 = auto):", xalign=0)
        spin_hdr = Gtk.SpinButton.new_with_range(0, 10, 1)
        spin_hdr.set_value(settings.header_columns or 0)
        grid.attach(lbl_hdr, 0, 3, 1, 1)
        grid.attach(spin_hdr, 1, 3, 1, 1)

        # Action Buttons
        dialog.add_button("Reset Defaults", Gtk.ResponseType.REJECT)
        dialog.add_button("Save as Default", Gtk.ResponseType.APPLY)
        dialog.add_button("Arrange Now", Gtk.ResponseType.OK)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)

        dialog.show_all()

        response = dialog.run()

        if response in (Gtk.ResponseType.OK, Gtk.ResponseType.APPLY):
            settings.node_spacing = int(spin_node.get_value())
            settings.layer_spacing = int(spin_layer.get_value())
            settings.direction = combo_dir.get_active_text() or "RIGHT"
            hdr_val = int(spin_hdr.get_value())
            settings.header_columns = hdr_val if hdr_val > 0 else None
            settings.save()

            if response == Gtk.ResponseType.OK:
                page = main_window.current_page
                flow_graph = page.flow_graph if page else None
                if flow_graph:
                    auto_arrange_flowgraph_gui(
                        flow_graph,
                        main_window,
                        page,
                        config=LayoutConfig.from_settings(settings)
                    )

        elif response == Gtk.ResponseType.REJECT:
            default_settings = AutoArrangeSettings()
            default_settings.save()

        dialog.destroy()

    except Exception as exc:
        log.exception("Error opening Auto-Arrange Settings Dialog: %s", exc)


def patch_grc() -> bool:
    """
    Patches gnuradio.grc.gui modules to inject the Auto Arrange action, settings dialog,
    menu items, toolbar button, and shortcuts.
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
        full_settings_action_name = f"app.{SETTINGS_ACTION_NAME}"

        # 1. Register Actions in Actions namespace
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

        if full_settings_action_name not in Actions.get_actions():
            settings_action = Actions.actions.register(
                name=full_settings_action_name,
                label="Auto _Arrange Settings...",
                tooltip="Configure block spacing and layout direction for Auto-Arrange",
                icon_name="preferences-system",
            )
        else:
            settings_action = Actions.actions[full_settings_action_name]

        setattr(Actions, "FLOW_GRAPH_AUTO_ARRANGE", auto_arrange_action)
        setattr(Actions, "FLOW_GRAPH_AUTO_ARRANGE_SETTINGS", settings_action)

        # 2. Add to Menu Bar: in _Edit menu and in _Tools menu
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
                edit_menu.append([auto_arrange_action, settings_action])

        if tools_menu is not None:
            found = any(
                auto_arrange_action in group if isinstance(group, list) else False
                for group in tools_menu
            )
            if not found:
                tools_menu.append([auto_arrange_action, settings_action])

        # 3. Add to Toolbar
        toolbar_found = any(
            auto_arrange_action in group if isinstance(group, list) else False
            for group in Bars.TOOLBAR_LIST
        )
        if not toolbar_found:
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
            elif action == settings_action or action == getattr(Actions, "FLOW_GRAPH_AUTO_ARRANGE_SETTINGS", None):
                main = self.main_window
                show_settings_dialog(main)
                return

            return orig_handle_action(self, action, *args)

        Application._handle_action = patched_handle_action

        _PATCHED = True
        log.info("Successfully patched GNU Radio Companion with Auto-Arrange addon.")
        return True

    except Exception as exc:
        log.warning("Could not patch GNU Radio Companion GUI: %s", exc)
        return False


def gnuradio_importable() -> bool:
    """True if the running interpreter can import GNU Radio Companion."""
    try:
        import gnuradio.grc  # noqa: F401
        return True
    except ImportError:
        return False


def find_grc_interpreter(grc_command: str = "gnuradio-companion") -> Optional[str]:
    """
    Locate the Python interpreter that owns GNU Radio by reading the shebang of the
    ``gnuradio-companion`` launcher on PATH. Returns None if it cannot be determined
    or if it is the interpreter already running (re-exec would not help).
    """
    exe = shutil.which(grc_command)
    if not exe:
        return None
    try:
        with open(exe, "rb") as fh:
            first_line = fh.readline()
    except OSError:
        return None
    if not first_line.startswith(b"#!"):
        return None
    parts = first_line[2:].decode("utf-8", errors="replace").strip().split()
    if not parts:
        return None
    interpreter = parts[0]
    # Handle "#!/usr/bin/env python3"
    if os.path.basename(interpreter) == "env" and len(parts) > 1:
        interpreter = shutil.which(parts[1]) or parts[1]
    if not os.path.isfile(interpreter):
        return None
    try:
        if os.path.samefile(interpreter, sys.executable):
            return None
    except OSError:
        pass
    return interpreter


def _package_shim_dir() -> Path:
    """
    Return a directory whose only content is a symlink to this package. Putting that
    directory (rather than our whole site-packages) on PYTHONPATH exposes only
    grc-autoarrange to the foreign interpreter, so we never shadow its own libraries.
    """
    pkg_dir = Path(__file__).resolve().parent
    cache_root = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    shim = cache_root / "grc-autoarrange" / "pythonpath"
    try:
        shim.mkdir(parents=True, exist_ok=True)
        link = shim / pkg_dir.name
        if link.is_symlink() or link.exists():
            if link.is_symlink() and link.resolve() == pkg_dir:
                return shim
            if link.is_dir() and not link.is_symlink():
                shutil.rmtree(link)
            else:
                link.unlink()
        link.symlink_to(pkg_dir, target_is_directory=True)
        return shim
    except OSError as exc:
        log.debug("Could not build package shim dir (%s); falling back to parent dir", exc)
        return pkg_dir.parent


def reexec_under_interpreter(interpreter: str, argv: Optional[List[str]] = None) -> None:
    """
    Replace the current process with ``interpreter`` running this tool's ``--gui`` mode.
    Only returns if exec fails.
    """
    flowgraphs = list(argv[1:]) if argv else []
    env = dict(os.environ)
    env[NO_REEXEC_ENV] = "1"
    shim = str(_package_shim_dir())
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = shim if not existing else shim + os.pathsep + existing
    cmd = [interpreter, "-m", "grc_autoarrange", "--gui", *flowgraphs]
    log.info("Re-launching under GNU Radio's interpreter: %s", " ".join(cmd))
    os.execve(interpreter, cmd, env)


def launch_grc(argv: Optional[List[str]] = None) -> int:
    """
    Launch GNU Radio Companion with the Auto-Arrange addon enabled.

    If GNU Radio is not importable from the current interpreter (typical when the tool
    is pip-installed into a venv while GNU Radio came from apt/conda), re-execute
    under the interpreter that owns ``gnuradio-companion``.
    """
    if not gnuradio_importable():
        if not os.environ.get(NO_REEXEC_ENV):
            interpreter = find_grc_interpreter()
            if interpreter:
                print(
                    f"grc-autoarrange: GNU Radio is not importable from {sys.executable}; "
                    f"re-launching under {interpreter}",
                    file=sys.stderr,
                )
                reexec_under_interpreter(interpreter, argv)
                print("grc-autoarrange: failed to re-launch under GNU Radio's interpreter", file=sys.stderr)
                return 1
        print(
            "grc-autoarrange: cannot import 'gnuradio' and no usable 'gnuradio-companion' was found on PATH.\n"
            "Install grc-autoarrange into the Python that provides GNU Radio, e.g.\n"
            "  pipx install --system-site-packages grc-autoarrange\n"
            "or ensure gnuradio-companion is on your PATH.",
            file=sys.stderr,
        )
        return 1

    patch_grc()
    from gnuradio.grc.main import main
    old_argv = sys.argv
    try:
        if argv is not None:
            sys.argv = argv
        return main() or 0
    finally:
        sys.argv = old_argv
