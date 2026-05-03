import json
from pathlib import Path
from typing import Any

from app.features.chat_analysis.domain.models import ExtractedFeatures, ScoreResult


DEFAULT_RULES = {
    "base_score": 60,
    "min_score": 5,
    "max_score": 100,
    "low_initiation": {"threshold": 25, "penalty": 10, "flag": "low effort"},
    "no_future_planning": {"threshold": 0, "penalty": 15, "flag": "avoidance"},
    "decreasing_message_length": {"penalty": 10, "flag": "low effort"},
    "high_sentiment": {"threshold": 0.60, "bonus": 15},
}


class ScoringEngine:
    def __init__(
        self,
        *,
        rules_path: str | Path | None = None,
        rules: dict[str, Any] | None = None,
    ) -> None:
        if rules is not None:
            self._rules = rules
        elif rules_path is not None:
            self._rules = json.loads(Path(rules_path).read_text(encoding="utf-8"))
        else:
            self._rules = DEFAULT_RULES

    def score(self, features: ExtractedFeatures) -> ScoreResult:
        score = self._rules["base_score"]
        flags: set[str] = set()

        low_initiation = self._rules["low_initiation"]
        if features.initiations < low_initiation["threshold"]:
            score -= low_initiation["penalty"]
            flags.add(low_initiation["flag"])

        no_future_planning = self._rules["no_future_planning"]
        if features.future_mentions <= no_future_planning["threshold"]:
            score -= no_future_planning["penalty"]
            flags.add(no_future_planning["flag"])

        decreasing_message_length = self._rules["decreasing_message_length"]
        if features.message_length_trend == "decreasing":
            score -= decreasing_message_length["penalty"]
            flags.add(decreasing_message_length["flag"])

        high_sentiment = self._rules["high_sentiment"]
        if features.sentiment_score >= high_sentiment["threshold"]:
            score += high_sentiment["bonus"]

        bounded_score = max(self._rules["min_score"], min(self._rules["max_score"], round(score)))
        return ScoreResult(score=bounded_score, flags=sorted(flags))
