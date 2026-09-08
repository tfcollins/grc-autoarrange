import pytest
from grc_autoarrange.layout_planner import LayoutPlanner, LayoutConfig, snap_to_grid


def test_snap_to_grid():
    assert snap_to_grid(0, 8) == 0
    assert snap_to_grid(7, 8) == 8
    assert snap_to_grid(9, 8) == 8
    assert snap_to_grid(12, 8) == 16
    assert snap_to_grid(103, 8) == 104


def test_layout_planner_header_and_dag():
    data = {
        "options": {
            "parameters": {"id": "test_top"},
            "states": {"coordinate": [0, 0]}
        },
        "blocks": [
            {
                "name": "var1",
                "id": "variable",
                "parameters": {"value": "100"},
                "states": {"coordinate": [0, 0]}
            },
            {
                "name": "var2",
                "id": "variable",
                "parameters": {"value": "200"},
                "states": {"coordinate": [0, 0]}
            },
            {
                "name": "src",
                "id": "analog_sig_source_x",
                "states": {"coordinate": [0, 0]}
            },
            {
                "name": "throttle",
                "id": "blocks_throttle",
                "states": {"coordinate": [0, 0]}
            },
            {
                "name": "sink",
                "id": "qtgui_sink_x",
                "states": {"coordinate": [0, 0]}
            }
        ],
        "connections": [
            ["src", "0", "throttle", "0"],
            ["throttle", "0", "sink", "0"]
        ]
    }

    planner = LayoutPlanner()
    coords = planner.arrange_flowgraph_data(data)

    # Verify all coordinates snapped to 8px grid
    for name, (x, y) in coords.items():
        assert x % 8 == 0, f"{name} x={x} is not multiple of 8"
        assert y % 8 == 0, f"{name} y={y} is not multiple of 8"

    # Verify options is top-left
    assert coords["options"] == (16, 16)

    # Variables should be positioned in header row
    assert coords["var1"][1] == 16
    assert coords["var2"][1] == 16

    # Signal DAG should be positioned below headers
    dag_y = min(coords["src"][1], coords["throttle"][1], coords["sink"][1])
    assert dag_y > coords["var1"][1]

    # Signal flow left to right
    assert coords["src"][0] < coords["throttle"][0]
    assert coords["throttle"][0] < coords["sink"][0]


def test_layout_planner_selection_only():
    data = {
        "options": {"parameters": {"id": "test"}},
        "blocks": [
            {"name": "b1", "id": "block1", "states": {"coordinate": [100, 100]}},
            {"name": "b2", "id": "block2", "states": {"coordinate": [200, 100]}},
            {"name": "unselected", "id": "block3", "states": {"coordinate": [500, 500]}}
        ],
        "connections": [
            ["b1", "0", "b2", "0"]
        ]
    }

    planner = LayoutPlanner()
    coords = planner.arrange_flowgraph_data(data, selected_block_names={"b1", "b2"})

    assert "b1" in coords
    assert "b2" in coords
    assert "unselected" not in coords
    assert coords["b1"][0] < coords["b2"][0]


def test_layout_planner_feedback_loop():
    # Feedback loop: src -> mixer -> filter -> mixer (feedback) -> sink
    data = {
        "options": {"parameters": {"id": "feedback_test"}},
        "blocks": [
            {"name": "src", "id": "source", "states": {"coordinate": [0, 0]}},
            {"name": "mixer", "id": "add_xx", "states": {"coordinate": [0, 0]}},
            {"name": "filter", "id": "iir_filter", "states": {"coordinate": [0, 0]}},
            {"name": "sink", "id": "sink", "states": {"coordinate": [0, 0]}}
        ],
        "connections": [
            ["src", "0", "mixer", "0"],
            ["mixer", "0", "filter", "0"],
            ["filter", "0", "mixer", "1"],  # Feedback edge
            ["filter", "0", "sink", "0"]
        ]
    }

    planner = LayoutPlanner()
    coords = planner.arrange_flowgraph_data(data)

    assert "src" in coords and "mixer" in coords and "filter" in coords and "sink" in coords
    assert coords["src"][0] <= coords["mixer"][0]
    assert coords["mixer"][0] <= coords["sink"][0]
