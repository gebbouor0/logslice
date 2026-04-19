"""Alert on log lines matching threshold-based rules."""
from dataclasses import dataclass, field
from typing import List, Optional
import re
from logslice.parser import LogLine


@dataclass
class AlertRule:
    name: str
    pattern: str
    threshold: int = 1
    description: str = ""


@dataclass
class Alert:
    rule: AlertRule
    matched_lines: List[LogLine] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.matched_lines)

    @property
    def triggered(self) -> bool:
        return self.count >= self.rule.threshold


@dataclass
class AlertResult:
    alerts: List[Alert] = field(default_factory=list)

    @property
    def triggered(self) -> List[Alert]:
        return [a for a in self.alerts if a.triggered]


def check_alerts(lines: List[LogLine], rules: List[AlertRule]) -> AlertResult:
    result = AlertResult()
    for rule in rules:
        alert = Alert(rule=rule)
        rx = re.compile(rule.pattern, re.IGNORECASE)
        for line in lines:
            if rx.search(line.message):
                alert.matched_lines.append(line)
        result.alerts.append(alert)
    return result


def format_alerts(result: AlertResult) -> str:
    lines = []
    for alert in result.triggered:
        lines.append(
            f"[ALERT] {alert.rule.name}: {alert.count} match(es) "
            f"(threshold={alert.rule.threshold})"
        )
        if alert.rule.description:
            lines.append(f"  {alert.rule.description}")
        for ll in alert.matched_lines:
            lines.append(f"  line {ll.line_number}: {ll.message}")
    return "\n".join(lines) if lines else "No alerts triggered."
