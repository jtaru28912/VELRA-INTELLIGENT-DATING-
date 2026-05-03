import re
from datetime import datetime

from app.features.chat_analysis.domain.models import NormalizedMessage


TIMESTAMPED_PATTERNS = (
    re.compile(
        r"^\[(?P<timestamp>[^\]]+)\]\s*(?P<sender>[^:]{1,32})\s*:\s*(?P<content>.+)$"
    ),
    re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?)\s*-\s*(?P<sender>[^:]{1,32})\s*:\s*(?P<content>.+)$"
    ),
)
SENDER_ONLY_PATTERN = re.compile(r"^(?P<sender>[^:]{1,32})\s*:\s*(?P<content>.+)$")
USER_ALIASES = {"you", "me", "self", "user", "client"}
COUNTERPART_ALIASES = {"them", "partner", "match", "other", "date"}
TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S",
)


class MessagePreprocessor:
    def normalize(self, messages: list[str]) -> list[NormalizedMessage]:
        parsed_messages: list[tuple[int, str | None, str, datetime | None]] = []
        discovered_senders: list[str] = []

        for index, raw_message in enumerate(messages):
            sender, content, timestamp = self._extract_parts(raw_message.strip())
            if sender and sender not in discovered_senders:
                discovered_senders.append(sender)
            parsed_messages.append((index, sender, content, timestamp))

        sender_map = self._build_sender_map(discovered_senders)
        normalized: list[NormalizedMessage] = []
        for index, sender, content, timestamp in parsed_messages:
            resolved_sender = sender_map.get(sender or "", "user" if index % 2 == 0 else "counterpart")
            normalized.append(
                NormalizedMessage(
                    index=index,
                    sender=resolved_sender,
                    content=content,
                    timestamp=timestamp,
                )
            )
        return normalized

    def _extract_parts(self, message: str) -> tuple[str | None, str, datetime | None]:
        for pattern in TIMESTAMPED_PATTERNS:
            match = pattern.match(message)
            if match:
                timestamp = self._parse_timestamp(match.group("timestamp"))
                return (
                    match.group("sender").strip().lower(),
                    match.group("content").strip(),
                    timestamp,
                )

        sender_match = SENDER_ONLY_PATTERN.match(message)
        if sender_match:
            return (
                sender_match.group("sender").strip().lower(),
                sender_match.group("content").strip(),
                None,
            )

        return None, message, None

    def _build_sender_map(self, discovered_senders: list[str]) -> dict[str, str]:
        sender_map: dict[str, str] = {}
        unresolved: list[str] = []

        for sender in discovered_senders:
            if sender in USER_ALIASES:
                sender_map[sender] = "user"
            elif sender in COUNTERPART_ALIASES:
                sender_map[sender] = "counterpart"
            else:
                unresolved.append(sender)

        if unresolved:
            sender_map[unresolved[0]] = "user"
        if len(unresolved) > 1:
            sender_map[unresolved[1]] = "counterpart"
        for sender in unresolved[2:]:
            sender_map[sender] = "counterpart"

        return sender_map

    def _parse_timestamp(self, raw_timestamp: str) -> datetime | None:
        candidate = raw_timestamp.strip()
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass

        for timestamp_format in TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(candidate, timestamp_format)
            except ValueError:
                continue
        return None
