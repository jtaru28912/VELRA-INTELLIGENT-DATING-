from sqlalchemy import select, update, cast, Uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.feedback.infrastructure.models import FeedbackRecord, LearningPatternRecord
from app.features.feedback.schemas import FeedbackRequest
from app.features.chat_analysis.infrastructure.models import ChatAnalysisRecord, TrainingData

class LearningLoopService:
    async def process_feedback(
        self,
        request: FeedbackRequest,
        session: AsyncSession,
        user_id: str,
    ) -> None:
        # 1. Store feedback
        feedback = FeedbackRecord(
            analysis_id=request.analysis_id,
            user_id=user_id,
            is_helpful=request.is_helpful,
        )
        session.add(feedback)
        
        # 2. Extract pattern from analysis
        # For the "Full Learning Loop", we find the analysis and extract the pattern
        analysis_stmt = select(ChatAnalysisRecord).where(ChatAnalysisRecord.id == request.analysis_id)
        analysis_res = await session.execute(analysis_stmt)
        analysis = analysis_res.scalar_one_or_none()
        
        if analysis and analysis.pattern:
            pattern_text = analysis.pattern
            # 3. Update learning_patterns table
            # Find if this pattern already exists
            pattern_stmt = select(LearningPatternRecord).where(LearningPatternRecord.pattern == pattern_text)
            pattern_res = await session.execute(pattern_stmt)
            existing_pattern = pattern_res.scalar_one_or_none()
            
            if existing_pattern:
                # Update stats
                new_occurrences = existing_pattern.occurrences + 1
                # Weighting the success rate: (existing * old_occ + current_feedback) / new_occ
                current_val = 1.0 if request.is_helpful else 0.0
                new_rate = (existing_pattern.success_rate * existing_pattern.occurrences + current_val) / new_occurrences
                
                existing_pattern.occurrences = new_occurrences
                existing_pattern.success_rate = new_rate
            else:
                # Create new pattern entry
                new_pattern = LearningPatternRecord(
                    pattern=pattern_text,
                    success_rate=1.0 if request.is_helpful else 0.0,
                    occurrences=1,
                )
                session.add(new_pattern)
        
        # 4. Update new Hybrid TrainingData loop
        training_stmt = update(TrainingData).where(
            (TrainingData.analysis_id == request.analysis_id) & (TrainingData.user_id == user_id)
        ).values(correctness=request.is_helpful)
        await session.execute(training_stmt)
        
        await session.commit()
