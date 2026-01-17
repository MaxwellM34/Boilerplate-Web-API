#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required env var: $name" >&2
    exit 1
  fi
}

require_env PROJECT_ID
WEB_BUCKET_NAME="${WEB_BUCKET_NAME:-${WEB_SERVICE_NAME:-}}"
if [[ -z "$WEB_BUCKET_NAME" ]]; then
  echo "Missing required env var: WEB_BUCKET_NAME (or WEB_SERVICE_NAME)" >&2
  exit 1
fi
WEB_BUCKET_NAME="${WEB_BUCKET_NAME#gs://}"

gcloud config set project "$PROJECT_ID"

if [[ ! -d out ]]; then
  echo "Missing build output: out/. Run 'npm run build' first." >&2
  exit 1
fi

gsutil -m rsync -r -c out/ "gs://$WEB_BUCKET_NAME"
