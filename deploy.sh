#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/api/deploy.sh"
"$SCRIPT_DIR/webapp/deploy.sh"
