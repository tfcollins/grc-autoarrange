from pathlib import Path
import pytest
from grc_autoarrange.cli import main, arrange_file
from grc_autoarrange.grc_parser import load_grc_file, save_grc_file


@pytest.fixture
def sample_grc_file(tmp_path: Path) -> Path:
    grc_data = {
        "options": {
            "parameters": {"id": "cli_test"},
            "states": {"coordinate": [0, 0]}
        },
        "blocks": [
            {
                "name": "src",
                "id": "analog_sig_source_x",
                "states": {"coordinate": [0, 0]}
            },
            {
                "name": "sink",
                "id": "qtgui_sink_x",
                "states": {"coordinate": [0, 0]}
            }
        ],
        "connections": [
            ["src", "0", "sink", "0"]
        ]
    }
    file_path = tmp_path / "flowgraph.grc"
    save_grc_file(grc_data, file_path)
    return file_path


def test_cli_output_file(sample_grc_file: Path, tmp_path: Path):
    out_file = tmp_path / "arranged.grc"
    ret = main([str(sample_grc_file), "-o", str(out_file)])
    assert ret == 0
    assert out_file.exists()

    data = load_grc_file(out_file)
    src_coord = data["blocks"][0]["states"]["coordinate"]
    sink_coord = data["blocks"][1]["states"]["coordinate"]
    assert src_coord[0] < sink_coord[0]


def test_cli_spacing_option(sample_grc_file: Path, tmp_path: Path):
    out_small = tmp_path / "small_spacing.grc"
    out_large = tmp_path / "large_spacing.grc"

    ret1 = main([str(sample_grc_file), "-o", str(out_small), "--spacing", "24"])
    ret2 = main([str(sample_grc_file), "-o", str(out_large), "--spacing", "120"])
    assert ret1 == 0 and ret2 == 0

    data_small = load_grc_file(out_small)
    data_large = load_grc_file(out_large)

    dist_small = data_small["blocks"][1]["states"]["coordinate"][0] - data_small["blocks"][0]["states"]["coordinate"][0]
    dist_large = data_large["blocks"][1]["states"]["coordinate"][0] - data_large["blocks"][0]["states"]["coordinate"][0]

    assert dist_large > dist_small


def test_cli_in_place(sample_grc_file: Path):
    ret = main([str(sample_grc_file), "--in-place"])
    assert ret == 0

    data = load_grc_file(sample_grc_file)
    src_coord = data["blocks"][0]["states"]["coordinate"]
    sink_coord = data["blocks"][1]["states"]["coordinate"]
    assert src_coord[0] < sink_coord[0]


def test_cli_dry_run(sample_grc_file: Path):
    ret = main([str(sample_grc_file), "--dry-run"])
    assert ret == 0
