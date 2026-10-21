# Lekcja 5: Sesje, tryb webowy, formattery, ciekawostki

**14:30–14:35 (5 min, pokaz prowadzącego)**

## Sesje

Sesje są zapisywane lokalnie i widać je z każdego klienta: TUI, webu i API.

- `opencode -c`: kontynuuj ostatnią sesję. `opencode -c --fork` robi to samo, ale w kopii.
- W TUI: `/sessions`, `/undo` (cofa też zmiany w plikach), `/compact`, `/share`.
- `opencode export <id>` / `opencode import plik.json`

## Tryb webowy

```bash
opencode web --port 4096
```

To ten sam serwer co `serve`, tylko z interfejsem w przeglądarce. Sesja zaczęta w TUI jest widoczna w webie.

## Formattery

W 1.x są **domyślnie wyłączone**. Włączasz je w `opencode.json` przez `"formatter": true`. Wtedy po każdej edycji pliku OpenCode uruchamia formatter, np. ruff albo prettier.

## Ciekawostki

- `opencode stats`: zużycie tokenów i koszt
- `!komenda` w TUI: wynik komendy trafia do kontekstu
- **Inny prompt systemowy dla każdej rodziny modeli:** OpenCode wybiera go po identyfikatorze modelu. Osobne prompty mają Claude, GPT (osobno GPT-4/o1/o3, Codex i GPT-6), Gemini, Kimi i Trinity, a reszta dostaje domyślny. Nasz `router/auto` też dostaje domyślny, niezależnie od tego, który model wybierze potem router.
- **Tytuł sesji generuje osobny prompt:** przy pierwszej wiadomości OpenCode równolegle wysyła drugie zapytanie z agentem `title` („You are a title generator…”) na modelu `small_model`. W logu routera widać wtedy dwa zapytania na jedną wiadomość.
