from __future__ import annotations

from pathlib import Path
import re
from typing import Any


class TrendAnalystAgent:
    """Read sales trend notes from data/sales_logs.md and summarize them."""

    def __init__(self, sales_log_path: str | Path = "data/sales_logs.md") -> None:
        self.sales_log_path = Path(sales_log_path)

    def load_sales_logs(self) -> list[dict[str, Any]]:
        """Parse the markdown sales log into structured records."""
        if not self.sales_log_path.exists():
            raise FileNotFoundError(
                f"Sales log not found at {self.sales_log_path}. "
                "Create data/sales_logs.md first."
            )

        records: list[dict[str, Any]] = []

        for raw_line in self.sales_log_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line.startswith("- "):
                continue

            fields: dict[str, str] = {}
            for token in line[2:].split(" | "):
                if ": " not in token:
                    continue
                key, value = token.split(": ", 1)
                fields[key.strip().lower()] = value.strip()

            if not fields:
                continue

            trend_text = fields.get("trend", "0%")
            trend_value = self._extract_percent(trend_text)

            records.append(
                {
                    "date": fields.get("date", ""),
                    "item": fields.get("item", ""),
                    "qty": int(fields["qty"]) if "qty" in fields and fields["qty"].isdigit() else None,
                    "trend": trend_text,
                    "trend_percent": trend_value,
                    "notes": fields.get("notes", ""),
                }
            )

        return records

    @staticmethod
    def _extract_percent(value: str) -> float:
        match = re.search(r"[-+]?\d+(?:\.\d+)?", value)
        if not match:
            raise ValueError(f"Could not find a numeric trend in: {value}")
        return float(match.group(0))

    def analyze(self) -> dict[str, Any]:
        """Return a concise trend summary for the current sales log."""
        records = self.load_sales_logs()
        if not records:
            return {
                "source": str(self.sales_log_path),
                "total_records": 0,
                "summary": "No sales records were found.",
                "negative_trends": [],
                "positive_trends": [],
            }

        negative_trends = [record for record in records if record["trend_percent"] < 0]
        positive_trends = [record for record in records if record["trend_percent"] > 0]

        worst_drop = min(negative_trends, key=lambda item: item["trend_percent"]) if negative_trends else None
        best_growth = max(positive_trends, key=lambda item: item["trend_percent"]) if positive_trends else None

        summary_lines = [
            f"Loaded {len(records)} sales records from {self.sales_log_path}.",
            f"Detected {len(negative_trends)} negative trend entries and {len(positive_trends)} positive trend entries.",
        ]

        if worst_drop:
            summary_lines.append(
                f"Biggest decline: {worst_drop['item']} at {worst_drop['trend_percent']:.0f}% "
                f"({worst_drop['notes']})."
            )

        if best_growth:
            summary_lines.append(
                f"Strongest increase: {best_growth['item']} at {best_growth['trend_percent']:.0f}% "
                f"({best_growth['notes']})."
            )

        return {
            "source": str(self.sales_log_path),
            "total_records": len(records),
            "summary": " ".join(summary_lines),
            "negative_trends": negative_trends,
            "positive_trends": positive_trends,
            "worst_drop": worst_drop,
            "best_growth": best_growth,
        }

    def report(self) -> str:
        """Return a readable summary string for the analyst."""
        return self.analyze()["summary"]


if __name__ == "__main__":
    analyst = TrendAnalystAgent()
    print(analyst.report())
    print("\nDetailed records:")
    for record in analyst.load_sales_logs():
        print(f"- {record['date']} | {record['item']} | QTY {record['qty']} | TREND {record['trend']} | NOTES {record['notes']}")
