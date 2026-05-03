import json
import random
import os

def generate_synthetic_data(num_rows=1000):
    dataset = []
    
    for _ in range(num_rows):
        initiations = random.randint(10, 90)
        avg_reply_delay = random.randint(1, 10)
        sentiment_score = round(random.uniform(-1.0, 1.0), 2)
        future_mentions = random.randint(0, 5)
        seriousness_score = random.randint(10, 100)
        
        if initiations < 40 and avg_reply_delay > 6:
            interest = "low"
        elif initiations > 60 and future_mentions > 2:
            interest = "high"
        else:
            interest = "medium"
            
        row = {
            "initiations": initiations,
            "avg_reply_delay": avg_reply_delay,
            "sentiment_score": sentiment_score,
            "future_mentions": future_mentions,
            "interest_level": interest,
            "seriousness_score": seriousness_score
        }
        dataset.append(row)

    return dataset

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "training_dataset.json")
    
    data = generate_synthetic_data(1000)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Generated {len(data)} rows at {out_path}")
