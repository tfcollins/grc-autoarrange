import pytest
from grc_autoarrange.elk_engine import ElkEngine, ElkNode, ElkEdge, ElkPort, ElkLayoutOptions


def test_elk_engine_basic():
    engine = ElkEngine()
    nodes = [
        ElkNode(id="src", width=100, height=50),
        ElkNode(id="sink", width=100, height=50)
    ]
    edges = [
        ElkEdge(id="e1", source="src", target="sink")
    ]
    res = engine.layout(nodes, edges)

    assert "src" in res.node_positions
    assert "sink" in res.node_positions
    src_x, src_y = res.node_positions["src"]
    sink_x, sink_y = res.node_positions["sink"]

    # In RIGHT direction, sink should be to the right of source
    assert sink_x > src_x


def test_elk_engine_port_ordering():
    engine = ElkEngine()
    nodes = [
        ElkNode(
            id="node_in",
            width=120,
            height=100,
            ports=[
                ElkPort(id="in0", side="WEST", x=-8.0, y=20.0),
                ElkPort(id="in1", side="WEST", x=-8.0, y=60.0)
            ]
        ),
        ElkNode(id="src0", width=80, height=40, ports=[ElkPort(id="out", side="EAST", x=80.0, y=16.0)]),
        ElkNode(id="src1", width=80, height=40, ports=[ElkPort(id="out", side="EAST", x=80.0, y=16.0)])
    ]
    edges = [
        ElkEdge(id="e1", source="src0", target="node_in", source_port="out", target_port="in0"),
        ElkEdge(id="e2", source="src1", target="node_in", source_port="out", target_port="in1")
    ]
    res = engine.layout(nodes, edges)

    assert res.node_positions["src0"][1] <= res.node_positions["src1"][1]


def test_elk_engine_custom_direction():
    engine = ElkEngine()
    nodes = [
        ElkNode(id="top", width=100, height=50),
        ElkNode(id="bottom", width=100, height=50)
    ]
    edges = [
        ElkEdge(id="e1", source="top", target="bottom")
    ]
    opts = ElkLayoutOptions(direction="DOWN")
    res = engine.layout(nodes, edges, options=opts)

    top_y = res.node_positions["top"][1]
    bottom_y = res.node_positions["bottom"][1]
    assert bottom_y > top_y
