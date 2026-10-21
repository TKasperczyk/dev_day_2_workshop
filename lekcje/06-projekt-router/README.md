# Lekcja 6: Projekt: router LLM z klasyfikatorem

**14:35–14:57 (22 min)**

## Cel

Rozumiesz, co robi router z `router/`, i rozbudowujesz go za pomocą OpenCode, używając agenta i skilla z poprzednich lekcji.

## Co robi router

1. **Maskuje** (`masking.py`): regexy podmieniają klucze, tokeny i hasła na `[MASKED:<rodzaj>]`.
2. **Klasyfikuje** (`classifier.py`): zwraca `safety` (`ok`/`block`) i `complexity` (`simple`/`code`/`reasoning`).
3. **Blokuje albo wybiera model**: przy `block` od razu odmawia, przy `ok` wybiera model według `complexity`.
4. **Loguje** jedną linię na zapytanie: safety, complexity, model, czas klasyfikacji, co zamaskował i prompt.

Jeśli klasyfikator nie odpowie, zapytanie przechodzi na model `code` (fail-open).

Router działa od lekcji 1. Konfiguracja jest w `router/.env`, a po każdej zmianie trzeba zrestartować router.

## Ćwiczenie 1: obserwacja (5 min)

```bash
bash lekcje/06-projekt-router/prompty.sh
```

[`prompty.sh`](prompty.sh) wysyła po jednym prompcie każdego rodzaju: `simple`, `code`, `reasoning`, z sekretem i dwa niebezpieczne. Patrz w log routera:

- Czy `complexity` i wybrany `model` się zgadzają?
- Czy w `prompt=` sekret jest zamaskowany?
- Czy niebezpieczne prompty mają `safety=block`?

## Ćwiczenie 2: rozbudowa (15 min)

Dodaj maskowanie tokenów Slacka (`xoxb-...`). Jeśli zacząłeś to w lekcji 3, dokończ tutaj.

1. **plan** (Tab): poproś o plan zmiany.
2. **build**: niech wprowadzi zmianę. Sam użyje skilla `dodaj-wzorzec-maskowania`.
3. `@reviewer przejrzyj zmianę`
4. Sprawdź testy: `cd router && uv run pytest -q`.

Dla chętnych:

- **Jev zamiast LLM:** w `router/.env` ustaw `CLASSIFIER=jev` i `TYPESAFE_API_KEY`, zrestartuj router, uruchom znowu `prompty.sh` i porównaj `classify_ms`.
- **Fail-closed:** gdy klasyfikator nie odpowie, blokuj zamiast przepuszczać.
- **Endpoint `/stats`:** liczniki safety, complexity i wybranych modeli.
