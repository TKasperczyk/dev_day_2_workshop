import json

import httpx
import pytest
from fastapi.testclient import TestClient

import app as router_app
import classifier

calls = []


def upstream(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    calls.append(body)
    if body["model"] == classifier.CLASSIFIER_MODEL:
        text = body["messages"][1]["content"]
        if "garbage" in text:
            content = "nie wiem"
        elif "rm -rf" in text:
            content = '{"safety": "block", "reason": "destrukcyjne", "complexity": "simple"}'
        else:
            content = '{"safety": "ok", "reason": "", "complexity": "reasoning"}'
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})
    if body.get("stream"):
        async def sse():
            yield b"data: {\"x\": 1}\n\n"
            yield b"data: [DONE]\n\n"

        return httpx.Response(200, content=sse(), headers={"content-type": "text/event-stream"})
    return httpx.Response(200, json={"model": body["model"]})


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    calls.clear()
    classifier._cache.clear()
    with TestClient(router_app.app) as c:
        c.app.state.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream), base_url="http://up")
        yield c


def ask(client, text, stream=False):
    return client.post("/v1/chat/completions", json={"model": "auto", "stream": stream, "messages": [{"role": "user", "content": text}]})


def test_routes_by_complexity(client):
    resp = ask(client, "zaprojektuj architekturę")
    assert resp.json()["model"] == router_app.MODELS["reasoning"]


def test_block_does_not_call_model(client):
    resp = ask(client, "zrób rm -rf na repo")
    assert "Zablokowane przez router: destrukcyjne" in resp.json()["choices"][0]["message"]["content"]
    assert [c["model"] for c in calls] == [classifier.CLASSIFIER_MODEL]


def test_block_streams_valid_sse(client):
    resp = ask(client, "rm -rf /", stream=True)
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert resp.text.endswith("data: [DONE]\n\n")


def test_secret_never_leaves(client):
    ask(client, "mój klucz to sk-or-v1-" + "a" * 40)
    assert all("sk-or-v1" not in json.dumps(c) for c in calls)


def test_classifier_garbage_falls_back_to_code(client):
    resp = ask(client, "garbage")
    assert resp.json()["model"] == router_app.MODELS["code"]


def test_stream_passthrough(client):
    resp = ask(client, "cześć", stream=True)
    assert resp.text == "data: {\"x\": 1}\n\ndata: [DONE]\n\n"


def test_classifies_once_per_prompt(client):
    ask(client, "to samo")
    ask(client, "to samo")
    assert [c["model"] for c in calls].count(classifier.CLASSIFIER_MODEL) == 1


def jev(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    calls.append(body)
    if "timeout" in body["state"]:
        raise httpx.ReadTimeout("za wolno")
    block = "rm -rf" in body["state"]
    return httpx.Response(200, json={"model": "jev-1.13.0", "answers": {
        "safety": {"type": "choice", "choice": "block" if block else "ok", "probabilities": {"block": 0.97 if block else 0.01, "ok": 0.03 if block else 0.99}},
        "complexity": {"type": "choice", "choice": "simple", "probabilities": {"simple": 0.9, "code": 0.1, "reasoning": 0.0}},
    }})


@pytest.fixture
def jev_client(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")
    monkeypatch.setattr(router_app, "CLASSIFIER", "jev")
    monkeypatch.setattr(classifier, "CLASSIFIER", "jev")
    calls.clear()
    classifier._cache.clear()
    with TestClient(router_app.app) as c:
        c.app.state.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream), base_url="http://up")
        c.app.state.jev = httpx.AsyncClient(transport=httpx.MockTransport(jev), base_url="http://jev")
        yield c


def test_jev_routes_by_choice(jev_client):
    resp = ask(jev_client, "co to jest SSE?")
    assert resp.json()["model"] == router_app.MODELS["simple"]
    assert calls[0]["questions"].keys() == {"safety", "complexity"}


def test_jev_block_reports_probability(jev_client):
    resp = ask(jev_client, "zrób rm -rf na repo")
    assert "Zablokowane przez router: jev p(block)=0.97" in resp.json()["choices"][0]["message"]["content"]


def test_jev_error_falls_back_to_code(jev_client):
    resp = ask(jev_client, "timeout")
    assert resp.json()["model"] == router_app.MODELS["code"]


def test_subagent_hint_is_not_classified(client):
    client.post("/v1/chat/completions", json={"model": "auto", "messages": [{"role": "user", "content": [
        {"type": "text", "text": "@reviewer sprawdź router"},
        {"type": "text", "text": " Use the above message and context to generate a prompt and call the task tool with subagent: reviewer"},
    ]}]})
    assert calls[0]["messages"][1]["content"] == "@reviewer sprawdź router"
    assert "subagent: reviewer" in json.dumps(calls[1]["messages"])
