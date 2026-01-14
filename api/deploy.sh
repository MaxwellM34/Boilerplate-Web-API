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
require_env REGION
require_env API_SERVICE_NAME
require_env API_ENV

gcloud config set project "$PROJECT_ID"

gcloud run deploy "$API_SERVICE_NAME" \
  --allow-unauthenticated \
  --source . \
  --region "$REGION" \
  --set-env-vars "ENV=$API_ENV" \
  --command uvicorn \
  --args main:app,--host,0.0.0.0,--port,8080
