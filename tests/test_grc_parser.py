from pathlib import Path
import pytest
from grc_autoarrange.grc_parser import (
    load_grc_file,
    save_grc_file,
    dump_grc_string,
    estimate_block_dimensions,
)


def test_parser_load_and_dump(tmp_path: Path):
    grc_sample = {
        "options": {
            "parameters": {"id": "test_fg", "title": "Test Title"},
            "states": {"coordinate": [8, 8], "rotation": 0, "state": "enabled"}
        },
        "blocks": [
            {
                "name": "samp_rate",
                "id": "variable",
                "parameters": {"value": "32000"},
                "states": {"coordinate": [200, 10], "rotation": 0, "state": "enabled"}
            }
        ],
        "connections": [],
        "metadata": {"file_format": 1}
    }

    test_file = tmp_path / "sample.grc"
    save_grc_file(grc_sample, test_file)
    assert test_file.exists()

    loaded = load_grc_file(test_file)
    assert loaded["options"]["parameters"]["id"] == "test_fg"
    assert len(loaded["blocks"]) == 1
    assert loaded["blocks"][0]["name"] == "samp_rate"


def test_estimate_block_dimensions():
    opt_block = {"id": "options", "name": "options"}
    assert estimate_block_dimensions(opt_block) == (160, 80)

    var_block = {"id": "variable", "name": "sampling_rate", "parameters": {"value": "1000000"}}
    w, h = estimate_block_dimensions(var_block)
    assert w >= 160
    assert h == 64

    proc_block = {
        "id": "analog_sig_source_x",
        "name": "sig_src",
        "parameters": {"freq": "1000", "amp": "1"}
    }
    pw, ph = estimate_block_dimensions(proc_block, sink_count=0, source_count=1)
    assert pw >= 160
    assert ph >= 64
