import asyncio
import json
import os
import sys

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so that `app` is importable whether
# this script is run directly (python ml/retrain_model.py) or scheduled
# internally.  This MUST happen before any `from app.*` imports.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import pandas as pd
import joblib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Import the model and settings from the app
from app.core.config import get_settings
from app.features.chat_analysis.infrastructure.models import TrainingData

async def retrain():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 1. Fetch Feedback Data
    async with async_session() as session:
        # Fetch rows where user gave feedback (correctness is not None)
        stmt = select(TrainingData).where(TrainingData.correctness != None)
        result = await session.execute(stmt)
        feedback_rows = result.scalars().all()

    if not feedback_rows:
        print("No new feedback data to retrain model.")
        return

    # 2. Load Original Dataset
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "training_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        original_data = json.load(f)
    
    df_original = pd.DataFrame(original_data)

    # 3. Process Feedback data into training format
    feedback_list = []
    for row in feedback_rows:
        # If correctness is True, the prediction was right. 
        # If correctness is False, we might need a way to know the *actual* label.
        # For simplicity in this version, we only use rows marked as Correct to reinforce.
        # Or better: The feedback could include the correct label. 
        # (For now, let's assume correctness=True means 'interest_level' was 'prediction')
        if row.correctness:
            data = row.features.copy()
            data['interest_level'] = row.prediction
            feedback_list.append(data)

    if not feedback_list:
        print("No positive feedback to retrain.")
        return

    df_feedback = pd.DataFrame(feedback_list)
    
    # 4. Merge and Shuffle
    df_combined = pd.concat([df_original, df_feedback], ignore_index=True)
    df_combined = df_combined.sample(frac=1).reset_index(drop=True)

    # 5. Train Model
    features = ['initiations', 'avg_reply_delay', 'sentiment_score', 'future_mentions']
    X = df_combined[features]
    
    le = LabelEncoder()
    y = le.fit_transform(df_combined['interest_level'])
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # 6. Save Updated Model
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump({
        'model': clf,
        'label_encoder': le,
        'features': features
    }, model_path)
    
    print(f"Retrained model with {len(feedback_list)} new samples. Saved to {model_path}")

if __name__ == "__main__":
    asyncio.run(retrain())
