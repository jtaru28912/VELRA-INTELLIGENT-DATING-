import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.cache import RedisCache

async def rate_limiter(request: Request):
    user = getattr(request.state, "user", None)
    # Fallback to IP if user isn't assigned yet, though the endpoint requires auth:
    identifier = user.id if user else request.client.host
    
    cache: RedisCache = request.app.state.cache
    if cache._client is None:
        return # Skip rate limiting if redis is down
    
    current_minute = int(time.time() / 60)
    key = f"rate_limit:{identifier}:{current_minute}"
    
    try:
         # Increment and set TTL if new
         pipe = cache._client.pipeline()
         pipe.incr(key)
         pipe.expire(key, 60)
         results = await pipe.execute()
         request_count = results[0]
         
         if request_count > 10:
             raise HTTPException(
                 status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                 detail="Rate limit exceeded. Maximum 10 requests per minute."
             )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Ignore redis errors so the app keeps functioning
        pass
