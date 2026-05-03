import json
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

def train():
    # 1. load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "training_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # 2. preprocess
    features = ['initiations', 'avg_reply_delay', 'sentiment_score', 'future_mentions']
    X = df[features]
    
    # 3. encode labels
    le = LabelEncoder()
    y = le.fit_transform(df['interest_level'])
    
    # 4. train RandomForestClassifier
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # 5. evaluate accuracy
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")
    
    # 6. save model -> ml/model.pkl using joblib
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump({
        'model': clf,
        'label_encoder': le,
        'features': features
    }, model_path)
    print(f"Saved model to {model_path}")

if __name__ == "__main__":
    train()
