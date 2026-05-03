from app.features.chat_analysis.application.feature_extractor import FeatureExtractor
from app.features.chat_analysis.application.preprocessor import MessagePreprocessor


def test_feature_extractor_with_timestamps_and_labels() -> None:
    messages = [
        "[2026-04-19 09:00] You: Morning! how are you?",
        "[2026-04-19 09:10] Them: Good :) excited for the weekend",
        "[2026-04-19 09:11] You: Nice, should we plan dinner?",
        "[2026-04-19 09:15] Them: Yes definitely let's do it",
    ]

    normalized = MessagePreprocessor().normalize(messages)
    features = FeatureExtractor().extract(normalized)

    assert features.avg_reply_time == 6.0
    assert features.initiations == 50.0
    assert features.message_length_trend == "increasing"
    assert features.sentiment_score > 0.65
    assert features.future_mentions >= 2


def test_feature_extractor_without_metadata_uses_deterministic_fallback() -> None:
    messages = ["Hey", "Hi there", "Want to catch up later?", "Sure"]

    normalized = MessagePreprocessor().normalize(messages)
    features = FeatureExtractor().extract(normalized)

    assert [message.sender for message in normalized] == [
        "user",
        "counterpart",
        "user",
        "counterpart",
    ]
    assert features.avg_reply_time == 0.0
    assert features.initiations == 50.0
    assert features.message_length_trend in {"increasing", "decreasing"}
