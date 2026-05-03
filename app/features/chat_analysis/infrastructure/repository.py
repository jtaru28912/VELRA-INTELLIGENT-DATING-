from typing import Any
from sqlalchemy import select, cast, Uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openai_client import OpenAIUsage
from app.features.chat_analysis.domain.models import ExtractedFeatures, ScoreResult
from app.features.chat_analysis.infrastructure.models import ChatAnalysisRecord, Credit
from app.features.chat_analysis.schemas import AnalyzeChatRequest, AnalyzeChatResponse


class ChatAnalysisRepository:
    async def get_by_request_hash(
        self,
        session: AsyncSession,
        request_hash: str,
    ) -> ChatAnalysisRecord | None:
        statement = select(ChatAnalysisRecord).where(ChatAnalysisRecord.request_hash == request_hash)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create_analysis(
        self,
        *,
        session: AsyncSession,
        request_hash: str,
        request: AnalyzeChatRequest,
        features: ExtractedFeatures,
        score_result: ScoreResult,
        response: AnalyzeChatResponse,
        usage: dict[str, int] | Any,
        user_id: str,
    ) -> ChatAnalysisRecord:
        record = ChatAnalysisRecord(
            user_id=user_id,
            request_hash=request_hash,
            context=request.context,
            messages=request.messages,
            features=features.to_dict(),
            flags=score_result.flags,
            seriousness_score=response.seriousness_score,
            interest_level=response.interest_level,
            pattern=response.behavioral_pattern,
            insights=" ".join(response.suggestions),
            suggested_action=response.date_strategy.justification,
            prompt_tokens=usage.get("prompt_tokens", 0) if isinstance(usage, dict) else usage.prompt_tokens,
            completion_tokens=usage.get("completion_tokens", 0) if isinstance(usage, dict) else usage.completion_tokens,
            total_tokens=usage.get("total_tokens", 0) if isinstance(usage, dict) else usage.total_tokens,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    async def get_user_history(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> list[ChatAnalysisRecord]:
        statement = (
            select(ChatAnalysisRecord)
            .where(ChatAnalysisRecord.user_id == user_id)
            .order_by(ChatAnalysisRecord.created_at.desc())
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    async def get_user_credits(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> Credit | None:
        statement = select(Credit).where(Credit.user_id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def initialize_credits(
        self,
        session: AsyncSession,
        user_id: str,
        initial_amount: int = 5,
    ) -> Credit:
        from datetime import datetime, timezone
        credit = Credit(
            user_id=user_id, 
            remaining=initial_amount,
            last_reset=datetime.now(timezone.utc)
        )
        session.add(credit)
        await session.commit()
        await session.refresh(credit)
        return credit

    async def delete_analysis(self, session: AsyncSession, user_id: str, analysis_id: str) -> bool:
        from app.features.chat_analysis.infrastructure.models import ChatAnalysisRecord
        from sqlalchemy import delete
        statement = delete(ChatAnalysisRecord).where(
            ChatAnalysisRecord.id == analysis_id,
            ChatAnalysisRecord.user_id == user_id
        )
        result = await session.execute(statement)
        await session.commit()
        return result.rowcount > 0
