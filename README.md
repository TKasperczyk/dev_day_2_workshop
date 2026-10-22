## DevDay II — warsztat OpenCode

**22.10.2026, 14:00–15:00, 42 Warsaw**

## Agenda

| Godzina | Temat | Materiały |
|---|---|---|
| 14:00 | Start, sprawdzenie setupu | [01-start-setup](lekcje/01-start-setup/) |
| 14:03 | Narzędzia, agenci wbudowani i własni | [02-narzedzia-i-agenci](lekcje/02-narzedzia-i-agenci/) |
| 14:13 | Skille | [03-skille](lekcje/03-skille/) |
| 14:20 | Tryb serwerowy i API | [04-serwer-i-api](lekcje/04-serwer-i-api/) |
| 14:30 | Sesje i tryb webowy, formattery, ciekawostki | [05-sesje-web-formattery](lekcje/05-sesje-web-formattery/) |
| 14:35 | Projekt: router LLM z klasyfikatorem | [06-projekt-router](lekcje/06-projekt-router/) |
| 14:57 | Q&A | [07-qa](lekcje/07-qa/) |

## Przygotowanie

Zrób to wcześniej.

**1. OpenCode**

```bash
curl -fsSL https://opencode.ai/install | bash
opencode --version   # wymagana wersja 1.x
```

**2. Python ≥ 3.11 + uv**

```bash
python3 --version
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**3. Model AI.** Klucz OpenRouter dostaniesz na warsztacie, przed nim nie musisz niczego zakładać. Klucz trafia do routera (`OPENROUTER_API_KEY` w `router/.env`), OpenCode łączy się z routerem przez `opencode.json`.

**4. Tryb serwerowy działa**

```bash
opencode serve --port 4096
# w drugim terminalu:
curl -s localhost:4096/session
```

**5. Repo** (materiały pojawią się tuż przed warsztatem, sklonujesz je na starcie)

```bash
git clone https://github.com/mateury/dev_day_2_workshop
```

### Checklista

- [ ] `opencode --version` pokazuje 1.x
- [ ] Python ≥ 3.11, `uv --version`
- [ ] `opencode` uruchamia się (TUI startuje)
- [ ] `curl localhost:4096/session` zwraca JSON
- [ ] `git` działa (repo sklonujesz na starcie warsztatu)

## Projekt: router LLM z klasyfikatorem

Samodzielna aplikacja w Pythonie (FastAPI, katalog `router/`), niezależna od OpenCode. Wystawia API zgodne z OpenAI i przekazuje zapytania do OpenRouter. OpenCode jest tylko jednym z klientów: łączy się z nią jako custom provider (`opencode.json`).

1. **Maskowanie sekretów:** regexy podmieniają klucze, tokeny i hasła na `[MASKED:<rodzaj>]` we wszystkich wiadomościach, zanim cokolwiek wyjdzie z laptopa.
2. **Klasyfikator:** mały model dostaje ostatnią wiadomość usera i zwraca `{"safety": "ok|block", "reason", "complexity": "simple|code|reasoning"}`.
3. **`block`:** router odpowiada odmową z powodem, model nie jest wołany.
4. **`ok`:** router wybiera model według `complexity` i przepuszcza odpowiedź (także streaming).
5. **Log:** jedna linia na zapytanie (safety, complexity, model, czas klasyfikacji, co zamaskowano).

```bash
cd router               # klucze są w router/.env
uv run --env-file .env uvicorn app:app --port 8000
# w katalogu głównym repo (opencode.json wskazuje na router):
opencode
```

**OpenCode poza repo.** `opencode.json` z repo działa tylko wtedy, gdy uruchamiasz OpenCode w katalogu repo (albo w jego podkatalogu). Jeśli chcesz używać routera w innym katalogu, skopiuj konfigurację do globalnej:

```bash
mkdir -p ~/.config/opencode
cp opencode.json ~/.config/opencode/opencode.json
```

Jeśli masz już globalny `opencode.json` albo `opencode.jsonc`, nie nadpisuj go. Dopisz do niego tylko `model`, `small_model` i `provider.router`. Po warsztacie usuń te wpisy, bo bez działającego routera OpenCode nie będzie miał modelu.

Modele ustawiasz zmiennymi `CLASSIFIER_MODEL`, `MODEL_SIMPLE`, `MODEL_CODE`, `MODEL_REASONING` (w `.env`). Testy: `uv run pytest -q`.

Klasyfikator przełączasz zmienną `CLASSIFIER`: `llm` (domyślnie, mały model w OpenRouter) albo `jev` ([Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) od TypeSafe, typowana decyzja z prawdopodobieństwem w ~70–500 ms, wymaga `TYPESAFE_API_KEY`). Porównaj `classify_ms` w logu.
