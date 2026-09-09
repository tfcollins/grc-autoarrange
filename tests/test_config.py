from pathlib import Path
import pytest
from grc_autoarrange.config import AutoArrangeSettings
from grc_autoarrange.layout_planner import LayoutConfig, LayoutPlanner


def test_auto_arrange_settings_defaults():
    settings = AutoArrangeSettings()
    assert settings.node_spacing == 48
    assert settings.layer_spacing == 64
    assert settings.direction == "RIGHT"
    assert settings.block_spacing == 48


def test_auto_arrange_settings_block_spacing_property():
    settings = AutoArrangeSettings()
    settings.block_spacing = 80
    assert settings.node_spacing == 80
    assert settings.layer_spacing == int(80 * 1.33)


def test_auto_arrange_settings_save_and_load(tmp_path: Path):
    cfg_file = tmp_path / "test_settings.json"
    settings = AutoArrangeSettings(node_spacing=72, layer_spacing=120, direction="DOWN")
    settings.save(cfg_file)

    assert cfg_file.exists()
    loaded = AutoArrangeSettings.load(cfg_file)
    assert loaded.node_spacing == 72
    assert loaded.layer_spacing == 120
    assert loaded.direction == "DOWN"


def test_layout_config_block_spacing_init():
    config = LayoutConfig(block_spacing=96)
    assert config.node_spacing == 96
    assert config.layer_spacing == int(96 * 1.33)
