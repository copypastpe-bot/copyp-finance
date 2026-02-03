#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env.local ]; then
  echo "Missing .env.local (create it based on .env.local.example)" >&2
  exit 1
fi

set -a
source .env.local
set +a

if [ -x ".venv/bin/python" ]; then
  exec .venv/bin/python -m bot.main
fi

exec python3 -m bot.main
