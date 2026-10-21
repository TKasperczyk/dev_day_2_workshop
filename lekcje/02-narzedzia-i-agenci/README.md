# Lekcja 2: Narzędzia, agenci wbudowani i własni

**14:03–14:13 (10 min)**

## Cel

Rozumiesz, jak model korzysta z narzędzi, czym różni się agent `primary` od `subagent`, i używasz własnego agenta z ograniczonymi uprawnieniami.

## Narzędzia

Model nic nie robi sam, tylko wywołuje narzędzia, a OpenCode je wykonuje: `read`, `grep`, `glob`, `edit`, `write`, `bash`, `task` (subagent), `skill`, `webfetch` i inne. Kolejne narzędzia dochodzą z serwerów MCP i pluginów.

O każdym narzędziu decydujesz uprawnieniem: `allow`, `ask` albo `deny`. Przykład w `opencode.json`:

```json
"permission": { "bash": { "*": "ask", "git status": "allow", "rm *": "deny" } }
```

Wygrywa **ostatnia** pasująca reguła, więc ogólne reguły dawaj na początek.

## Agenci wbudowani

| Agent | Tryb | Opis |
|---|---|---|
| `build` | primary | domyślny, ma wszystkie narzędzia |
| `plan` | primary | tylko planuje, nie edytuje |
| `general` | subagent | zadania wieloetapowe |
| `explore` | subagent | szybkie przeszukiwanie kodu |

- **Tab** przełącza agentów `primary`.
- Subagenta wołasz przez `@nazwa`, a model może go też uruchomić sam narzędziem `task`.

## Własny agent

Agent to plik `.opencode/agents/<nazwa>.md`: we frontmatterze jest konfiguracja, a pod nim prompt.

Gotowy przykład: [`.opencode/agents/reviewer.md`](../../.opencode/agents/reviewer.md). To subagent, który nie może edytować plików, a w bashu wolno mu tylko `git diff/log/show/status` i `pytest`.

## Ćwiczenie

1. `opencode agent list`: sprawdź, czy jest `reviewer (subagent)`.
2. W TUI: `@reviewer przejrzyj router/masking.py`.
3. Poproś go o poprawkę w pliku. Powinien dostać odmowę.
