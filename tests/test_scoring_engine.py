from app.features.chat_analysis.application.scoring import DEFAULT_RULES, ScoringEngine
from app.features.chat_analysis.domain.models import ExtractedFeatures


def test_scoring_engine_applies_configurable_rules() -> None:
    engine = ScoringEngine(rules=DEFAULT_RULES)
    features = ExtractedFeatures(
        avg_reply_time=0.0,
        initiations=25.0,
        message_length_trend="decreasing",
        sentiment_score=0.8,
        future_mentions=0,
    )

    result = engine.score(features)

    assert result.score == 50
    assert result.flags == ["avoidance", "low effort"]


def test_scoring_engine_rewards_positive_signals() -> None:
    engine = ScoringEngine(rules=DEFAULT_RULES)
    features = ExtractedFeatures(
        avg_reply_time=5.0,
        initiations=60.0,
        message_length_trend="increasing",
        sentiment_score=0.9,
        future_mentions=2,
    )

    result = engine.score(features)

    assert result.score == 75
    assert result.flags == []
