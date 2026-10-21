# /// script
# dependencies = ["httpx"]
# ///
"""Wysyła prompt do serwera OpenCode i wypisuje odpowiedź. Użycie: uv run ask.py "pytanie" """

import sys

import httpx

c = httpx.Client(base_url="http://localhost:4096", timeout=300)
sid = c.post("/session", json={"title": "skrypt"}).json()["id"]
r = c.post(f"/session/{sid}/message", json={"parts": [{"type": "text", "text": sys.argv[1]}]}).json()
print("".join(p.get("text", "") for p in r["parts"] if p["type"] == "text"))
