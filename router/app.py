"""Proxy zgodne z OpenAI: maskuje sekrety, klasyfikuje prompt, blokuje albo wybiera model w OpenRouter."""

import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from starlette.background import BackgroundTask

from classifier import CLASSIFIER, JEV_URL, classify
from masking import mask_messages

OPENROUTER_URL = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1")
MODELS = {
    "simple": os.environ.get("MODEL_SIMPLE", "nvidia/nemotron-3.5-lightning"),
    "code": os.environ.get("MODEL_CODE", "poolside/laguna-s-2.1"),
    "reasoning": os.environ.get("MODEL_REASONING", "nvidia/nemotron-3-super-120b-a12b"),
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("router")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("Ustaw OPENROUTER_API_KEY")
    app.state.client = httpx.AsyncClient(
        base_url=OPENROUTER_URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        timeout=httpx.Timeout(300, connect=10),
    )
    if CLASSIFIER == "jev":
        if not os.environ.get("TYPESAFE_API_KEY"):
            raise SystemExit("CLASSIFIER=jev wymaga TYPESAFE_API_KEY")
        app.state.jev = httpx.AsyncClient(
            base_url=JEV_URL, headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"}
        )
    log.info("klasyfikator: %s", CLASSIFIER)
    yield
    await app.state.client.aclose()
    if CLASSIFIER == "jev":
        await app.state.jev.aclose()


app = FastAPI(lifespan=lifespan)

# Przy @subagencie opencode dokleja tę instrukcję jako osobną część wiadomości. Klasyfikator brał ją za prompt injection.
SUBAGENT_HINT = "Use the above message and context to generate a prompt and call the task tool with subagent:"


def last_user_text(messages: list[dict]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content")
            if isinstance(content, str):
                return content
            return "\n".join(
                p.get("text", "") for p in content or []
                if p.get("type") == "text" and not p.get("text", "").strip().startswith(SUBAGENT_HINT)
            )
    return ""


def refusal(stream: bool, reason: str) -> Response:
    text = f"Zablokowane przez router: {reason}"
    cid, created = f"chatcmpl-{uuid.uuid4().hex}", int(time.time())
    if not stream:
        return JSONResponse({
            "id": cid, "object": "chat.completion", "created": created, "model": "router",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        })
    chunks = [
        {"choices": [{"index": 0, "delta": {"role": "assistant", "content": text}, "finish_reason": None}]},
        {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
    ]
    body = "".join(
        f"data: {json.dumps({'id': cid, 'object': 'chat.completion.chunk', 'created': created, 'model': 'router', **c})}\n\n"
        for c in chunks
    ) + "data: [DONE]\n\n"
    return Response(body, media_type="text/event-stream")


@app.get("/v1/models")
async def models():
    return {"object": "list", "data": [{"id": "auto", "object": "model", "owned_by": "router"}]}


@app.post("/v1/chat/completions")
async def chat(request: Request):
    client: httpx.AsyncClient = request.app.state.client
    body = await request.json()
    body["messages"], masked = mask_messages(body.get("messages", []))

    prompt = last_user_text(body["messages"])
    verdict = await classify(request.app.state.jev if CLASSIFIER == "jev" else client, prompt)
    model = MODELS[verdict.complexity]
    # prompt po maskowaniu, %r trzyma go w jednej linii
    log.info(
        "safety=%s complexity=%s model=%s classify_ms=%d%s masked=%s reason=%s prompt=%r",
        verdict.safety, verdict.complexity, model if verdict.safety == "ok" else "-",
        verdict.ms, " (fallback)" if verdict.fallback else "", ",".join(masked) or "-", verdict.reason, prompt,
    )
    if verdict.safety == "block":
        return refusal(bool(body.get("stream")), verdict.reason)

    body["model"] = model
    if body.get("stream"):
        upstream = await client.send(client.build_request("POST", "/chat/completions", json=body), stream=True)
        return StreamingResponse(
            upstream.aiter_raw(),
            status_code=upstream.status_code,
            media_type=upstream.headers.get("content-type", "text/event-stream"),
            background=BackgroundTask(upstream.aclose),
        )
    resp = await client.post("/chat/completions", json=body)
    return Response(resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
