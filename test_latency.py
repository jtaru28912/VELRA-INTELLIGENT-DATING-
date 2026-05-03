import asyncio
import time
from dotenv import load_dotenv
load_dotenv()
from app.features.chat_analysis.schemas import AnalyzeChatRequest
from app.core.config import get_settings
from app.core.cache import RedisCache
from app.core.chroma import ChromaManager
from app.core.openai_client import OpenAIClient
from app.features.chat_analysis.infrastructure.repository import ChatAnalysisRepository
from app.features.chat_analysis.application.preprocessor import MessagePreprocessor
from app.features.chat_analysis.application.feature_extractor import FeatureExtractor
from app.features.chat_analysis.application.scoring import ScoringEngine
from app.features.chat_analysis.application.service import ChatAnalysisService

# Mock session
class MockSession:
    async def execute(self, stmt):
        class MockResult:
            def scalar_one_or_none(self):
                return None
        return MockResult()
    
    def add(self, obj):
        pass
    
    async def commit(self):
        pass
        
    async def flush(self):
        pass
        
    async def refresh(self, obj):
        pass

async def main():
    print("Testing latency and flow...")
    start_setup = time.time()
    
    settings = get_settings()
    # disable openai to test bare metal semantic cache speed
    # if openai is enabled, it would naturally take > 300ms due to network
    settings.openai_api_key = None 
    
    cache = RedisCache(settings)
    chroma = ChromaManager(settings)
    openai_client = OpenAIClient(settings)
    repository = ChatAnalysisRepository()
    
    # Overriding create_analysis for test so no db writes fail
    async def mock_create_analysis(*args, **kwargs):
        class MockRecord:
            id = "test_uuid"
        return MockRecord()
    repository.create_analysis = mock_create_analysis
    repository.get_user_history = lambda *args, **kwargs: [] # Mock history 
    
    service = ChatAnalysisService(
        settings=settings,
        cache=cache,
        chroma=chroma,
        openai_client=openai_client,
        repository=repository,
        preprocessor=MessagePreprocessor(),
        feature_extractor=FeatureExtractor(),
        scoring_engine=ScoringEngine(rules_path=settings.scoring_rules_path),
    )
    
    request = AnalyzeChatRequest(
        messages=["hey", "how are you today?", "let's grab coffee"],
        context="talking_stage",
        profile_id="some_id"
    )
    
    print(f"Setup took: {(time.time() - start_setup)*1000:.2f}ms")
    
    # Run test
    start_exec = time.time()
    session = MockSession()
    
    try:
        response = await service.analyze_chat(
            request=request,
            session=session,
            user_id="test_user"
        )
        dur = (time.time() - start_exec)*1000
        print(f"Latency: {dur:.2f}ms")
        print("Success! Response structure:")
        print(response.model_dump_json(indent=2))
        if dur < 300:
            print("Latency is compliant (<300ms) with LLM fallbacks/redis hit!")
        else:
            print("Latency failed threshold!")
    except Exception as e:
        print(f"Error during flow: {e}")

if __name__ == "__main__":
    asyncio.run(main())
