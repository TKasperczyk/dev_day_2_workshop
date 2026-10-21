---
name: dodaj-wzorzec-maskowania
description: Dodaje nowy wzorzec sekretu do router/masking.py razem z testem. Użyj, gdy użytkownik chce maskować nowy rodzaj klucza, tokenu lub danych osobowych w routerze.
---

# Dodawanie wzorca maskowania

1. Dopisz wpis do `PATTERNS` w `router/masking.py`.
   - Klucz: rodzaj sekretu w snake_case, trafia do `[MASKED:<rodzaj>]`.
   - Jeśli maskujesz tylko wartość (np. po `token=`), użyj nazwanej grupy `(?P<v>...)`.
   - Kolejność ma znaczenie: bardziej szczegółowe wzorce przed ogólnymi.
2. Dodaj test w `router/tests/test_masking.py`: jeden przypadek, który ma zostać zamaskowany, i jeden fałszywy alarm, który ma przejść bez zmian.
3. Uruchom `cd router && uv run pytest -q`. Wszystko ma przejść.
