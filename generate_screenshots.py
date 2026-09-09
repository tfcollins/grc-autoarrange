"""
Generates high-resolution Before and After screenshots using GNU Radio Companion's Cairo renderer.
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
from gnuradio.grc.gui import Utils, Actions
from grc_autoarrange.layout_planner import LayoutPlanner
from grc_autoarrange.gui_addon import patch_grc

DEMO_FLOWGRAPH = {
    'options': {
        'parameters': {
            'author': 'GNU Radio',
            'category': '[GRC Hier Blocks]',
            'id': 'fm_demod_demo',
            'title': 'FM Demodulator & Audio Pipeline',
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
            'states': {'coordinate': [520, 380], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'quad_rate',
            'id': 'variable',
            'parameters': {'value': '480e3'},
            'states': {'coordinate': [100, 390], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'audio_decim',
            'id': 'variable',
            'parameters': {'value': '10'},
            'states': {'coordinate': [760, 40], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'analog_sig_source_c_0',
            'id': 'analog_sig_source_x',
            'parameters': {
                'type': 'complex',
                'freq': '100e3',
                'amp': '1.0',
                'samp_rate': 'samp_rate',
                'waveform': 'analog.GR_COS_WAVE'
            },
            'states': {'coordinate': [620, 180], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'blocks_throttle_0',
            'id': 'blocks_throttle',
            'parameters': {
                'type': 'complex',
                'samples_per_second': 'samp_rate'
            },
            'states': {'coordinate': [40, 160], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'low_pass_filter_0',
            'id': 'low_pass_filter',
            'parameters': {
                'type': 'fir_filter_ccf',
                'decim': '5',
                'gain': '1.0',
                'samp_rate': 'samp_rate',
                'cutoff_freq': '100e3',
                'width': '10e3'
            },
            'states': {'coordinate': [320, 120], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'analog_wfm_rcv_0',
            'id': 'analog_wfm_rcv',
            'parameters': {
                'quad_rate': 'quad_rate',
                'audio_decimation': 'audio_decim'
            },
            'states': {'coordinate': [120, 20], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'qtgui_time_sink_x_0',
            'id': 'qtgui_time_sink_x',
            'parameters': {
                'type': 'float',
                'size': '1024',
                'samp_rate': '48e3',
                'name': '"Demodulated Audio"'
            },
            'states': {'coordinate': [740, 180], 'rotation': 0, 'state': 'enabled'}
        },
        {
            'name': 'qtgui_freq_sink_x_0',
            'id': 'qtgui_freq_sink_x',
            'parameters': {
                'type': 'complex',
                'fftsize': '1024',
                'samp_rate': 'samp_rate',
                'name': '"RF Spectrum"'
            },
            'states': {'coordinate': [440, 320], 'rotation': 0, 'state': 'enabled'}
        }
    ],
    'connections': [
        ['analog_sig_source_c_0', '0', 'blocks_throttle_0', '0'],
        ['blocks_throttle_0', '0', 'low_pass_filter_0', '0'],
        ['blocks_throttle_0', '0', 'qtgui_freq_sink_x_0', '0'],
        ['low_pass_filter_0', '0', 'analog_wfm_rcv_0', '0'],
        ['analog_wfm_rcv_0', '0', 'qtgui_time_sink_x_0', '0']
    ],
    'metadata': {'file_format': 1}
}


def main():
    patch_grc()

    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

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

    messy_file = "/tmp/grc_messy_demo.grc"
    with open(messy_file, 'w') as f:
        yaml.dump(DEMO_FLOWGRAPH, f, sort_keys=False)

    # 1. Load Messy Flowgraph
    main_window.new_page(messy_file, show=True)
    fg_before = main_window.current_page.flow_graph
    fg_before.update()

    before_png = str(assets_dir / "grc_before_arrange.png")
    print(f"Rendering {before_png}...")
    Utils.make_screenshot(fg_before, before_png, transparent_bg=False)

    # 2. Auto-Arrange
    planner = LayoutPlanner()
    new_coords = planner.arrange_flowgraph_data(DEMO_FLOWGRAPH)
    
    arranged_data = dict(DEMO_FLOWGRAPH)
    if 'options' in new_coords:
        arranged_data['options']['states']['coordinate'] = list(new_coords['options'])
    for b in arranged_data['blocks']:
        bname = b.get('name')
        if bname in new_coords:
            b['states']['coordinate'] = list(new_coords[bname])

    arranged_file = "/tmp/grc_arranged_demo.grc"
    with open(arranged_file, 'w') as f:
        yaml.dump(arranged_data, f, sort_keys=False)

    # 3. Load Arranged Flowgraph
    main_window.new_page(arranged_file, show=True)
    fg_after = main_window.current_page.flow_graph
    fg_after.update()

    after_png = str(assets_dir / "grc_after_arrange.png")
    print(f"Rendering {after_png}...")
    Utils.make_screenshot(fg_after, after_png, transparent_bg=False)

    print("Screenshots successfully generated!")


if __name__ == '__main__':
    main()
