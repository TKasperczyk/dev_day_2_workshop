# Lekcja 3: Skille

**14:13–14:20 (7 min)**

## Cel

Rozumiesz, czym skill różni się od agenta i `AGENTS.md`, i widzisz, jak model sam go ładuje.

## Czym jest skill

Skill to instrukcja ładowana **tylko wtedy, gdy jest potrzebna**. Na starcie model widzi wyłącznie `name` i `description`. Pełną treść dociąga narzędziem `skill`, kiedy zadanie pasuje do opisu.

| | Kiedy trafia do kontekstu | Do czego |
|---|---|---|
| `AGENTS.md` | zawsze | reguły projektu |
| agent | gdy go wybierzesz | rola i uprawnienia |
| skill | gdy model uzna, że pasuje | procedura „jak zrobić X” |

Skill to plik `.opencode/skills/<nazwa>/SKILL.md`. OpenCode czyta też skille z `~/.claude/skills` i `~/.agents/skills`, więc działają skille z Claude Code.

Gotowy przykład: [`.opencode/skills/dodaj-wzorzec-maskowania/SKILL.md`](../../.opencode/skills/dodaj-wzorzec-maskowania/SKILL.md).

Najważniejsze jest `description`: bez niego skill w ogóle nie trafi do modelu. Ma mówić, **co** skill robi i **kiedy** go użyć.

## Ćwiczenie

1. `opencode debug skill | grep maskowania`: sprawdź, czy skill jest wykryty.
2. W TUI napisz: „maskuj też tokeny Slacka (xoxb-...)”.
3. Sprawdź w historii, że model wywołał `skill`, a potem dodał wzorzec razem z testem.

Ta zmiana to też zadanie z lekcji 6. Jeśli tu nie zdążysz, dokończysz ją tam.
