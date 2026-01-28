#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env.local ]; then
  echo "Missing .env.local (create it based on .env.local.example)" >&2
  exit 1
fi

set -a
source .env.local
set +a

python -m bot.main
