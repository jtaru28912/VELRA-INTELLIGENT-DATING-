from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class NormalizedMessage:
    index: int
    sender: str
    content: str
    timestamp: datetime | None


@dataclass(slots=True)
class ExtractedFeatures:
    avg_reply_time: float
    initiations: float
    message_length_trend: str
    sentiment_score: float
    future_mentions: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScoreResult:
    score: int
    flags: list[str]
