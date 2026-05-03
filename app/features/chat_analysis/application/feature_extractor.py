import re

from app.features.chat_analysis.domain.models import ExtractedFeatures, NormalizedMessage


POSITIVE_WORDS = {
    "love",
    "excited",
    "great",
    "good",
    "amazing",
    "happy",
    "nice",
    "fun",
    "enjoy",
    "cute",
    "sweet",
    "definitely",
    "yes",
    "bet",
    "valid",
    "fire",
    "real",
    "fr",
    "ong",
    " slay",
    "goated",
    "acha",
    "shukriya",
    "dhanyawad",
    "mast",
    "badhiya",
    "sahi",
    "sundar",
    "pyaar",
    "mohabbat",
}
NEGATIVE_WORDS = {
    "busy",
    "later",
    "maybe",
    "tired",
    "sorry",
    "can't",
    "cannot",
    "hard",
    "bad",
    "no",
    "nah",
    "bekar",
    "ganda",
    "nhi",
    "nahi",
    "na",
    "mana",
}
POSITIVE_EMOJIS = {":)", ":-)", "❤️", "😊", "😂", "😍", "😉", "👍", "🔥", "✨", "✅", "💯"}
NEGATIVE_EMOJIS = {":(", ":-(", "😕", "😒", "👎", "🚫", "❌"}
# Modern ambiguous emojis that are often used hyperbolically in positive/playful contexts
HYPERBOLIC_EMOJIS = {"💀", "😭", "🤡", "🫠", "🤏", "🚩"}
FUTURE_PATTERN = re.compile(
    r"\b(tomorrow|weekend|next\s+(week|month)|later|soon|plan|plans|planned|will|let's|lets|see you|trip|date)\b",
    re.IGNORECASE,
)
TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


class FeatureExtractor:
    def extract(self, messages: list[NormalizedMessage]) -> ExtractedFeatures:
        avg_reply_time = self._avg_reply_time(messages)
        initiations = self._initiation_ratio(messages)
        message_length_trend = self._message_length_trend(messages)
        sentiment_score = self._sentiment_score(messages)
        future_mentions = self._future_mentions(messages)

        return ExtractedFeatures(
            avg_reply_time=avg_reply_time,
            initiations=initiations,
            message_length_trend=message_length_trend,
            sentiment_score=sentiment_score,
            future_mentions=future_mentions,
        )

    def _avg_reply_time(self, messages: list[NormalizedMessage]) -> float:
        gaps: list[float] = []
        for previous, current in zip(messages, messages[1:]):
            if previous.sender == current.sender:
                continue
            if previous.timestamp is None or current.timestamp is None:
                continue

            delta_minutes = (current.timestamp - previous.timestamp).total_seconds() / 60
            if delta_minutes >= 0:
                gaps.append(delta_minutes)

        return round(sum(gaps) / len(gaps), 2) if gaps else 0.0

    def _initiation_ratio(self, messages: list[NormalizedMessage]) -> float:
        turns: list[str] = []
        previous_sender: str | None = None
        for message in messages:
            if message.sender != previous_sender:
                turns.append(message.sender)
                previous_sender = message.sender

        if not turns:
            return 0.0

        counterpart_turns = sum(1 for turn in turns if turn == "counterpart")
        return round((counterpart_turns / len(turns)) * 100, 2)

    def _message_length_trend(self, messages: list[NormalizedMessage]) -> str:
        target_messages = [message for message in messages if message.sender == "counterpart"] or messages
        lengths = [self._word_count(message.content) for message in target_messages]
        if len(lengths) < 2:
            return "increasing"

        x_values = list(range(len(lengths)))
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(lengths) / len(lengths)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, lengths))
        denominator = sum((x - x_mean) ** 2 for x in x_values) or 1.0
        slope = numerator / denominator
        return "increasing" if slope >= 0 else "decreasing"

    def _sentiment_score(self, messages: list[NormalizedMessage]) -> float:
        target_messages = [message for message in messages if message.sender == "counterpart"] or messages
        if not target_messages:
            return 0.5

        message_scores: list[float] = []
        for message in target_messages:
            tokens = TOKEN_PATTERN.findall(message.content.lower())
            token_score = 0
            for token in tokens:
                if token in POSITIVE_WORDS:
                    token_score += 1
                elif token in NEGATIVE_WORDS:
                    token_score -= 1

            emoji_score = sum(1 for emoji in POSITIVE_EMOJIS if emoji in message.content)
            emoji_score -= sum(1 for emoji in NEGATIVE_EMOJIS if emoji in message.content)
            
            # Hyperbolic emojis count as 'engagement high' but neutral sentiment
            # unless used in a toxic context (which the LLM will catch).
            # We give them a tiny boost to represent 'energy' without assuming sentiment.
            energy_score = sum(0.2 for emoji in HYPERBOLIC_EMOJIS if emoji in message.content)

            raw_score = token_score + emoji_score + energy_score
            normalized = max(0.0, min(1.0, 0.5 + (raw_score / max(len(tokens), 1)) * 0.5))
            message_scores.append(normalized)

        return round(sum(message_scores) / len(message_scores), 3)

    def _future_mentions(self, messages: list[NormalizedMessage]) -> int:
        target_messages = [message for message in messages if message.sender == "counterpart"] or messages
        count = 0
        for message in target_messages:
            count += len(FUTURE_PATTERN.findall(message.content))
        return count

    def _word_count(self, content: str) -> int:
        return len(TOKEN_PATTERN.findall(content))
