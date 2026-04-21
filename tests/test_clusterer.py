"""Tests for logslice.clusterer."""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.clusterer import (
    _fingerprint,
    cluster_lines,
    format_clusters,
    Cluster,
    ClusterResult,
)


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=None,
        level=None,
        line_number=n,
    )


def test_fingerprint_strips_numbers():
    assert "error connecting port" == _fingerprint("error connecting to port 8080")


def test_fingerprint_lowercases():
    fp = _fingerprint("ERROR Failed")
    assert fp == fp.lower()


def test_fingerprint_ignores_short_tokens():
    fp = _fingerprint("to be or not to be")
    assert fp == ""


def test_cluster_groups_similar_messages():
    lines = [
        make_line("error connecting to port 8080", 1),
        make_line("error connecting to port 9090", 2),
        make_line("error connecting to port 3000", 3),
    ]
    result = cluster_lines(lines)
    assert len(result) == 1
    assert len(result.clusters[0]) == 3


def test_cluster_singletons_go_to_unclustered():
    lines = [
        make_line("database connection failed", 1),
        make_line("disk write error occurred", 2),
    ]
    result = cluster_lines(lines, min_cluster_size=2)
    assert len(result.clusters) == 0
    assert len(result.unclustered) == 2


def test_cluster_min_size_respected():
    lines = [
        make_line("timeout waiting for response", 1),
        make_line("timeout waiting for response", 2),
        make_line("unique unrelated message here", 3),
    ]
    result = cluster_lines(lines, min_cluster_size=2)
    assert len(result) == 1
    assert len(result.unclustered) == 1


def test_cluster_result_total_lines():
    lines = [make_line(f"error processing request {i}", i) for i in range(5)]
    result = cluster_lines(lines, min_cluster_size=2)
    assert result.total_lines == 5


def test_cluster_sorted_by_size_descending():
    lines = (
        [make_line("alpha beta gamma delta", i) for i in range(3)]
        + [make_line(f"zebra yak xray {i}", i + 10) for i in range(5)]
    )
    result = cluster_lines(lines, min_cluster_size=2)
    sizes = [len(c) for c in result.clusters]
    assert sizes == sorted(sizes, reverse=True)


def test_format_clusters_contains_label():
    lines = [
        make_line("worker failed processing job", 1),
        make_line("worker failed processing job", 2),
    ]
    result = cluster_lines(lines)
    output = format_clusters(result)
    assert "worker" in output
    assert "Cluster 1" in output


def test_format_clusters_shows_unclustered():
    lines = [make_line("only one unique thing here", 1)]
    result = cluster_lines(lines, min_cluster_size=2)
    output = format_clusters(result)
    assert "Unclustered" in output


def test_cluster_empty_input():
    result = cluster_lines([])
    assert len(result) == 0
    assert result.total_lines == 0
