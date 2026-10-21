# Lekcja 1: Start i sprawdzenie setupu

**14:00–14:03 (3 min)**

## Cel

Masz działające OpenCode, sklonowane repo i uruchomiony router. Router jest potrzebny już od lekcji 2, bo bez niego OpenCode nie ma modelu.

## Kroki

```bash
git clone https://github.com/mateury/dev_day_2_workshop
cd dev_day_2_workshop

bash lekcje/01-start-setup/sprawdz-setup.sh
```

Skrypt [`sprawdz-setup.sh`](sprawdz-setup.sh) sprawdza wersje narzędzi, tryb serwerowy i czy w `router/.env` jest klucz OpenRouter. Wszystko powinno mieć ✅.

Uruchom router w osobnym terminalu i zostaw go włączonego do końca warsztatu:

```bash
cd router && uv run --env-file .env uvicorn app:app --port 8000
```

## Jak to się łączy

```
opencode ──(API zgodne z OpenAI)──▶ router :8000 ──▶ OpenRouter
                                    maskowanie, klasyfikator, wybór modelu
```

OpenCode wie o routerze z `opencode.json` (model `router/auto`). Klucz trafia tylko do routera.

**OpenCode poza repo.** `opencode.json` z repo działa tylko wtedy, gdy uruchamiasz OpenCode w katalogu repo (albo w jego podkatalogu). Jeśli chcesz używać routera w innym katalogu, skopiuj konfigurację do globalnej:

```bash
mkdir -p ~/.config/opencode
cp opencode.json ~/.config/opencode/opencode.json
```

Jeśli masz już globalny `opencode.json` albo `opencode.jsonc`, nie nadpisuj go. Dopisz do niego tylko `model`, `small_model` i `provider.router`. Po warsztacie usuń te wpisy, bo bez działającego routera OpenCode nie będzie miał modelu.
