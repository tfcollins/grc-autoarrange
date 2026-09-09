"""
Generates screenshots demonstrating the Configurable Block Spacing feature
(Settings Dialog, Compact Spacing, and Spacious Spacing).
"""

import sys
import os
import yaml
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GLib
from gnuradio import gr
from gnuradio.grc.gui.Platform import Platform
from gnuradio.grc.gui.Application import Application
from gnuradio.grc.gui.MainWindow import MainWindow
from gnuradio.grc.gui import Utils
from grc_autoarrange.layout_planner import LayoutPlanner, LayoutConfig
from grc_autoarrange.gui_addon import patch_grc

DEMO_FLOWGRAPH = {
    'options': {
        'parameters': {
            'author': 'GNU Radio',
            'category': '[GRC Hier Blocks]',
            'id': 'spacing_demo',
            'title': 'Configurable Spacing Flowgraph Demo',
            'generate_options': 'qt_gui'
        },
        'states': {
            'coordinate': [8, 8],
            'rotation': 0,
            'state': 'enabled'
        }
    },
    'blocks': [
        {
            'name': 'samp_rate',
            'id': 'variable',
            'parameters': {'value': '2.4e6'},
            'states': {'coordinate': [8, 8], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'center_freq',
            'id': 'variable',
            'parameters': {'value': '915e6'},
            'states': {'coordinate': [8, 8], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'sig_source',
            'id': 'analog_sig_source_x',
            'parameters': {
                'type': 'complex',
                'freq': '100e3',
                'amp': '1.0',
                'samp_rate': 'samp_rate'
            },
            'states': {'coordinate': [0, 0], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'throttle',
            'id': 'blocks_throttle',
            'parameters': {
                'type': 'complex',
                'samples_per_second': 'samp_rate'
            },
            'states': {'coordinate': [0, 0], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'lpf',
            'id': 'low_pass_filter',
            'parameters': {
                'type': 'fir_filter_ccf',
                'decim': '1',
                'gain': '1.0',
                'samp_rate': 'samp_rate',
                'cutoff_freq': '350e3',
                'width': '50e3'
            },
            'states': {'coordinate': [0, 0], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'time_sink',
            'id': 'qtgui_time_sink_x',
            'parameters': {
                'type': 'complex',
                'size': '1024',
                'samp_rate': 'samp_rate'
            },
            'states': {'coordinate': [0, 0], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'freq_sink',
            'id': 'qtgui_freq_sink_x',
            'parameters': {
                'type': 'complex',
                'fftsize': '1024',
                'samp_rate': 'samp_rate'
            },
            'states': {'coordinate': [0, 0], 'rotation': 0, 'state': 'enabled'}
        }
    ],
    'connections': [
        ['sig_source', '0', 'throttle', '0'],
        ['throttle', '0', 'lpf', '0'],
        ['lpf', '0', 'time_sink', '0'],
        ['lpf', '0', 'freq_sink', '0']
    ],
    'metadata': {'file_format': 1}
}


def render_flowgraph_to_file(data, output_png):
    platform = Platform(
        version=gr.version(),
        version_parts=(gr.major_version(), gr.api_version(), gr.minor_version()),
        prefs=gr.prefs(),
        install_prefix=gr.prefix()
    )
    platform.build_library()
    app = Application([], platform)
    main_window = MainWindow(app, platform)
    app.main_window = main_window

    tmp_grc = "/tmp/tmp_spacing_render.grc"
    with open(tmp_grc, 'w') as f:
        yaml.dump(data, f, sort_keys=False)

    main_window.new_page(tmp_grc, show=True)
    fg = main_window.current_page.flow_graph
    fg.update()
    Utils.make_screenshot(fg, output_png, transparent_bg=False)


def main():
    patch_grc()
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate Compact Layout (spacing = 24)
    planner_compact = LayoutPlanner(config=LayoutConfig(node_spacing=24, layer_spacing=40, header_gap_y=20))
    coords_compact = planner_compact.arrange_flowgraph_data(DEMO_FLOWGRAPH)
    data_compact = dict(DEMO_FLOWGRAPH)
    data_compact['options']['states']['coordinate'] = list(coords_compact['options'])
    for b in data_compact['blocks']:
        if b['name'] in coords_compact:
            b['states']['coordinate'] = list(coords_compact[b['name']])

    compact_png = str(assets_dir / "grc_spacing_compact.png")
    print(f"Rendering {compact_png}...")
    render_flowgraph_to_file(data_compact, compact_png)

    # 2. Generate Spacious Layout (spacing = 96)
    planner_spacious = LayoutPlanner(config=LayoutConfig(node_spacing=96, layer_spacing=130, header_gap_y=48))
    coords_spacious = planner_spacious.arrange_flowgraph_data(DEMO_FLOWGRAPH)
    data_spacious = dict(DEMO_FLOWGRAPH)
    data_spacious['options']['states']['coordinate'] = list(coords_spacious['options'])
    for b in data_spacious['blocks']:
        if b['name'] in coords_spacious:
            b['states']['coordinate'] = list(coords_spacious[b['name']])

    spacious_png = str(assets_dir / "grc_spacing_spacious.png")
    print(f"Rendering {spacious_png}...")
    render_flowgraph_to_file(data_spacious, spacious_png)

    print("Spacing comparison canvas screenshots generated successfully!")


if __name__ == '__main__':
    main()
