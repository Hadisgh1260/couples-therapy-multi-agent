import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI(
    title="Couples Therapy Gateway"
)

GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "").strip()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "couples-therapy-gateway"
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    payload: dict,
    authorization: str | None = Header(default=None),
    x_groq_api_key: str | None = Header(
        default=None,
        alias="X-Groq-API-Key"
    ),
):

    # Check Gateway API key
    if authorization != f"Bearer {GATEWAY_API_KEY}":
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid Gateway API key"
            }
        )

    # Check Groq API key
    if not x_groq_api_key:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Groq API key is missing"
            }
        )

    headers = {
        "Authorization": f"Bearer {x_groq_api_key.strip()}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:

        response = await client.post(
            GROQ_URL,
            headers=headers,
            json=payload,
        )

    return JSONResponse(
        status_code=response.status_code,
        content=response.json(),
    )