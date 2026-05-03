# Velra

Velra is a production-oriented FastAPI service for analyzing dating chat conversations. It uses a clean architecture flow of `router -> service -> repository`, async endpoints, PostgreSQL persistence, Redis caching, ChromaDB storage, and OpenAI-backed interpretation. A robust JWT Auth mechanism isolates user data inside PostgreSQL and ChromaDB for secure RAG processing.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy async + PostgreSQL
- Redis
- ChromaDB
- OpenAI Python SDK
- Scikit-learn, Pandas, Joblib (ML Engine)
- Pydantic v2
- passlib & PyJWT (Auth)

## Setup

1. Create a virtual environment and ensure dependencies are installed via requirements.
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate # Unix
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Environment Variables
Copy `.env.example` to `.env`. Ensure the following keys are populated:
- `DATABASE_URL`: async PostgreSQL connection string.
- `REDIS_URL`: Redis cache URL.
- `JWT_SECRET`: Secret Key for generation tokens.
- `OPENAI_API_KEY`: Required for live analysis fallback instead of deterministic generation.
- `USE_CHROMA_HTTP`: `true` connects to a Chroma HTTP service instance.

4. Start dependencies and API locally:
```bash
docker-compose up --build
```
    
## API Endpoints

### Auth Module

**`POST /auth/signup`**
```json
{
  "email": "user@velra.app",
  "password": "securepassword123"
}
```

**`POST /auth/login`**
Returns:
```json
{
  "access_token": "eyJhb...",
  "token_type": "bearer"
}
```

### Analysis Module (Requires `Authorization: Bearer <token>`)

**`POST /analyze-chat`**
Request:
```json
{
  "messages": [
    "[2026-04-19 09:00] You: hey, how's your day going?",
    "[2026-04-19 09:10] Them: pretty good :) how about you?"
  ],
  "context": "talking_stage"
}
```

Response:
```json
{
  "seriousness_score": 90,
  "interest_level": "high",
  "behavioral_pattern": ["consistent reciprocity"],
  "emotional_investment": "high",
  "risk_level": "low",
  "evidence": [
    "Replied in 2 minutes to a complex open-ended question.",
    "Used 3+ high-investment emojis (🔥, ✨).",
    "Made a specific future mention of a weekend plan."
  ],
  "reasoning": "The user is exhibiting high linguistic synchronization and proactive engagement velocity...",
  "date_strategy": {
    "budget": "$$",
    "type": "creative activity",
    "justification": "They appreciate novelty and show high intent."
  },
  "impression_strategy": ["Match their energy exactly", "Be slightly mysterious"],
  "suggestions": ["Recent travel stories", "Music tastes"],
  "replies": ["That sounds amazing! I'd love to go.", "I'm free on Friday ;)"],
  "effort_level": "balanced"
}
```

### Tips & Calculators Module

**`POST /tips/generate`**
Provides specific dating strategies (General or Personalized) based on chat context or target profiles.

**`POST /calculate/date`**
Optimizes date planning based on budget indicators and relationship intent.

### Social DNA Analysis
Leverages Gemini Search Grounding to evaluate digital fingerprints (Instagram, LinkedIn, etc.) and provides a narrative psychological evaluation.
*Note: A strict rate limit of 5 requests per day is enforced for Freemium users using Redis.*

## Cloud Deployment (Free-Tier Stack)

You can easily deploy Velra across free-tier hosting solutions to maintain a decoupled resilient application:

1. **PostgreSQL via Supabase**:
   - Create a free project on [Supabase](https://supabase.com).
   - Navigate to database settings and grab your PostgreSQL URI.
   - Adjust protocol to async driver: `postgresql+asyncpg://...`

2. **Redis via Upstash**:
   - Create a free tier Redis instance on [Upstash](https://upstash.com/).
   - Copy `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`.
   - Freemium rate limiting is automatically enforced at 5 requests/day.

3. **Backend Intelligence**:
   - Initial setup requires running the ML training script:
     ```bash
     python ml/train_model.py
     ```
   - Retraining for continuous learning can be scheduled as a cron job:
     ```bash
     python ml/retrain_model.py
     ```

4. **Backend via Render**:
   - Create a new "Web Service".
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - Paste all Environment overrides inside Render's Dashboard.
   - Set up the rendered Healthcheck endpoint -> `GET /health` to keep deployments stable.

4. **Frontend / Web Deployment** (Included React UI):
   - You can separately deploy the `frontend/` directory using platforms like Vercel or Render Static Pages by setting the root dir to `frontend` and the build script to `npm run build`.

## Testing

```bash
pytest
```
