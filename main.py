import secrets
import string
import redis
import uvicorn

from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import Response, RedirectResponse

app = FastAPI()

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


class CreateCodePayload(BaseModel):
    url: str


@app.post("/")
async def create_code(payload: CreateCodePayload):
    # Generate code
    characters = string.ascii_lowercase + string.digits
    code = "".join([secrets.choice(characters) for _ in range(8)])

    # Save code to Redis
    redis_client.set(code, payload.url)

    return code


@app.get("/{code}")
async def redirect_url(request: Request, code: str):
    url = redis_client.get(code)
    if url:
        return RedirectResponse(url)

    return Response(
        content="URL not found",
        status_code=404,
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
