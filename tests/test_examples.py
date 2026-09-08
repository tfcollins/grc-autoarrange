from pathlib import Path
import pytest
from grc_autoarrange.grc_parser import load_grc_file
from grc_autoarrange.layout_planner import LayoutPlanner


EXAMPLES_DIR = Path("/usr/share/gnuradio/examples")


def get_example_grc_files():
    if not EXAMPLES_DIR.exists():
        return []
    return list(EXAMPLES_DIR.glob("**/*.grc"))[:15]


@pytest.mark.parametrize("grc_path", get_example_grc_files(), ids=lambda p: p.name)
def test_real_grc_examples(grc_path: Path):
    data = load_grc_file(grc_path)
    planner = LayoutPlanner()
    coords = planner.arrange_flowgraph_data(data)

    assert "options" in coords
    assert coords["options"] == (16, 16)

    for name, (x, y) in coords.items():
        assert x % 8 == 0, f"Block {name} x={x} is not 8px grid aligned in {grc_path.name}"
        assert y % 8 == 0, f"Block {name} y={y} is not 8px grid aligned in {grc_path.name}"
        assert x >= 0, f"Block {name} has negative x={x}"
        assert y >= 0, f"Block {name} has negative y={y}"
