# Lekcja 4: Tryb serwerowy i API

**14:20–14:30 (10 min)**

## Cel

Wiesz, że TUI to tylko jeden z klientów serwera OpenCode, i sam wysyłasz prompt przez API.

## Architektura

```
opencode serve  (HTTP API + SSE)
   ▲     ▲      ▲
  TUI   web   skrypt / CI / bot
```

```bash
opencode serve --port 4096                              # samo API, bez interfejsu
opencode attach http://localhost:4096                   # TUI podpięte do tego serwera
opencode run --attach http://localhost:4096 "pytanie"   # jednorazowe zapytanie
```

Pełna specyfikacja: `curl -s localhost:4096/doc` (OpenAPI).

| Metoda | Ścieżka | Co robi |
|---|---|---|
| GET / POST | `/session` | lista sesji / nowa sesja |
| POST | `/session/{id}/message` | wysyła prompt i czeka na odpowiedź |
| POST | `/session/{id}/prompt_async` | wysyła prompt bez czekania |
| POST | `/session/{id}/abort` | przerywa |
| GET | `/event` | strumień zdarzeń (SSE) |

## Ćwiczenie

Uruchom serwer w katalogu głównym repo (`opencode serve --port 4096`), a w osobnym terminalu zdarzenia: `curl -N localhost:4096/event`.

[`ask.py`](ask.py) tworzy sesję i wysyła prompt przez API (`uv` sam zainstaluje `httpx`):

```bash
uv run lekcje/04-serwer-i-api/ask.py "co robi router/masking.py?"
```

Obserwuj, jak w terminalu z `/event` pojawiają się kolejne zdarzenia. Sesje utworzone przez API zobaczysz też w TUI pod `/sessions`.

## Bezpieczeństwo

API pozwala wykonywać komendy w powłoce. Jeśli wystawiasz serwer poza `127.0.0.1`, ustaw `OPENCODE_SERVER_PASSWORD`.
