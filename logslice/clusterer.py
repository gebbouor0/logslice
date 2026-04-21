"""Cluster log lines by message similarity using simple token fingerprinting."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from logslice.parser import LogLine


@dataclass
class Cluster:
    label: str
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class ClusterResult:
    clusters: List[Cluster]
    unclustered: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.clusters)

    @property
    def total_lines(self) -> int:
        return sum(len(c) for c in self.clusters) + len(self.unclustered)


_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMBER_RE = re.compile(r"\b\d+\b")


def _fingerprint(message: str) -> str:
    """Reduce a message to a stable key by stripping numbers and short tokens."""
    msg = _NUMBER_RE.sub("#", message)
    tokens = _TOKEN_RE.findall(msg)
    significant = [t.lower() for t in tokens if len(t) > 2]
    return " ".join(significant[:8])


def cluster_lines(
    lines: List[LogLine],
    min_cluster_size: int = 2,
) -> ClusterResult:
    """Group lines by message fingerprint; singletons go to unclustered."""
    buckets: Dict[str, List[LogLine]] = defaultdict(list)
    for line in lines:
        key = _fingerprint(line.message)
        buckets[key].append(line)

    clusters: List[Cluster] = []
    unclustered: List[LogLine] = []

    for key, members in buckets.items():
        if len(members) >= min_cluster_size:
            label = key if key.strip() else "(empty)"
            clusters.append(Cluster(label=label, lines=members))
        else:
            unclustered.extend(members)

    clusters.sort(key=lambda c: -len(c))
    return ClusterResult(clusters=clusters, unclustered=unclustered)


def format_clusters(result: ClusterResult) -> str:
    """Return a human-readable summary of clusters."""
    lines = []
    for i, cluster in enumerate(result.clusters, 1):
        lines.append(f"[Cluster {i}] ({len(cluster)} lines) pattern: {cluster.label!r}")
        for ll in cluster.lines:
            lines.append(f"  #{ll.line_number}: {ll.message}")
    if result.unclustered:
        lines.append(f"[Unclustered] ({len(result.unclustered)} lines)")
        for ll in result.unclustered:
            lines.append(f"  #{ll.line_number}: {ll.message}")
    return "\n".join(lines)
