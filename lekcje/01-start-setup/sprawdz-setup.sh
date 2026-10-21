#!/usr/bin/env bash
# Sprawdza checklistę warsztatu. Uruchom z katalogu głównym repo: bash lekcje/01-start-setup/sprawdz-setup.sh
set -u

ok() { echo "✅ $1"; }
fail() { echo "❌ $1"; FAILED=1; }
FAILED=0

v=$(opencode --version 2>/dev/null) && [[ $v == 1.* ]] && ok "opencode $v" || fail "opencode 1.x (jest: ${v:-brak})"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null && ok "$(python3 --version)" || fail "python3 >= 3.11"
uv --version >/dev/null 2>&1 && ok "$(uv --version)" || fail "uv"
git --version >/dev/null 2>&1 && ok "$(git --version)" || fail "git"

# Tryb serwerowy: używa działającego serwera na 4096 albo stawia tymczasowy.
PID=""
if ! curl -s -m 2 localhost:4096/session >/dev/null; then
  opencode serve --port 4096 >/dev/null 2>&1 &
  PID=$!
  for _ in $(seq 1 30); do curl -s -m 1 localhost:4096/session >/dev/null && break; sleep 0.5; done
fi
curl -s -m 2 localhost:4096/session | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null \
  && ok "curl localhost:4096/session zwraca JSON" || fail "curl localhost:4096/session"
[ -n "$PID" ] && kill "$PID"

[ -f router/.env ] && grep -q '^OPENROUTER_API_KEY=.' router/.env \
  && ok "router/.env z OPENROUTER_API_KEY" || fail "router/.env: brak OPENROUTER_API_KEY (git pull albo wpisz klucz)"

exit $FAILED
