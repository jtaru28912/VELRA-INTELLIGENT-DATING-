import asyncio
import logging
import json
import sys
import os
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.getcwd())

from app.core.config import get_settings
from app.core.openai_client import OpenAIClient
from app.features.chat_analysis.application.agents import StrategyGeneratorAgent

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def test_end_to_end():
    load_dotenv()
    settings = get_settings()
    
    # Initialize components
    client = OpenAIClient(settings)
    agent = StrategyGeneratorAgent(client)
    
    # Test data based on user's recent input
    history = "User: i hate u and never want to see u again"
    persona = "should i move on or wait for him to come back"
    features = {
        "avg_reply_time": 100.0,
        "initiations": 0.0,
        "message_length_trend": "decreasing",
        "sentiment_score": 0.1,
        "future_mentions": 0
    }
    
    print("\n--- STARTING END-TO-END TEST ---")
    try:
        response, usage = await agent.execute(
            features=features,
            prediction_interest="LOW",
            seriousness_score=10,
            history=history,
            persona=persona
        )
        
        print("\n--- TEST SUCCESSFUL ---")
        print(f"Seriousness Score: {response.seriousness_score}")
        print(f"Interest Level: {response.interest_level}")
        print(f"Psychological Insight: {response.psychological_insight}")
        print(f"Date Verdict: {'GO' if response.should_go_on_date else 'NO-GO'}")
        print(f"Evidence: {response.evidence}")
        print(f"Usage: {usage}")
        
        # Verify it's not a fallback
        if "Analysis failed" in response.date_strategy.justification:
            print("\nWARNING: FALLBACK DETECTED!")
        else:
            print("\nCONFIRMED: REAL ANALYSIS GENERATED.")
            
    except Exception as e:
        print(f"\n--- TEST FAILED ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
