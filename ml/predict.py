import joblib
import os

model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
_model_data = None

def get_model():
    global _model_data
    if _model_data is None:
        if os.path.exists(model_path):
            _model_data = joblib.load(model_path)
    return _model_data

def predict(features: dict) -> str:
    """
    features: {
        'initiations': int,
        'avg_reply_delay': float,
        'sentiment_score': float,
        'future_mentions': int
    }
    """
    model_data = get_model()
    if not model_data:
        return "medium" # Fallback if model not trained
        
    clf = model_data['model']
    le = model_data['label_encoder']
    feature_names = model_data['features']
    
    # ensure correct order
    x_input = [features.get(f, 0) for f in feature_names]
    
    # predict
    pred_idx = clf.predict([x_input])[0]
    return le.inverse_transform([pred_idx])[0]
