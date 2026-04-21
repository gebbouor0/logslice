"""Integration tests for clusterer: realistic mixed log input."""
from logslice.parser import LogLine
from logslice.clusterer import cluster_lines, format_clusters


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, level=None, line_number=n)


MESSAGES = [
    "timeout waiting for upstream service",
    "timeout waiting for upstream service",
    "timeout waiting for upstream service",
    "connection refused on port 5432",
    "connection refused on port 5433",
    "disk usage exceeded threshold 90%",
    "disk usage exceeded threshold 95%",
    "one-off anomaly detected in subsystem",
]


def _make_lines():
    return [make_line(m, i + 1) for i, m in enumerate(MESSAGES)]


def test_integration_cluster_count():
    result = cluster_lines(_make_lines(), min_cluster_size=2)
    assert len(result) >= 2


def test_integration_total_lines_preserved():
    lines = _make_lines()
    result = cluster_lines(lines, min_cluster_size=2)
    assert result.total_lines == len(lines)


def test_integration_format_no_error():
    result = cluster_lines(_make_lines(), min_cluster_size=2)
    output = format_clusters(result)
    assert isinstance(output, str)
    assert len(output) > 0


def test_integration_unclustered_singleton():
    result = cluster_lines(_make_lines(), min_cluster_size=2)
    # "one-off anomaly" should be unclustered
    unclustered_msgs = [ll.message for ll in result.unclustered]
    assert any("anomaly" in m for m in unclustered_msgs)


def test_integration_largest_cluster_first():
    result = cluster_lines(_make_lines(), min_cluster_size=2)
    if len(result.clusters) >= 2:
        assert len(result.clusters[0]) >= len(result.clusters[1])
