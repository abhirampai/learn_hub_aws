#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=authenticate_user.sh
source "$SCRIPT_DIR/authenticate_user.sh"

decode_jwt_payload() {
  local token="$1"

  TOKEN="$token" python3 - <<'PY'
import base64
import json
import os

token = os.environ["TOKEN"]
parts = token.split(".")

if len(parts) != 3:
    raise SystemExit("Invalid JWT: expected three dot-separated segments")

payload = parts[1]
payload += "=" * (-len(payload) % 4)

try:
    decoded = base64.urlsafe_b64decode(payload)
    claims = json.loads(decoded)
except (ValueError, json.JSONDecodeError) as error:
    raise SystemExit(f"Invalid JWT payload: {error}") from error

print(json.dumps(claims, indent=2, sort_keys=True))
PY
}

printf '\nID token claims:\n'
decode_jwt_payload "$ID_TOKEN"

printf '\nAccess token claims:\n'
decode_jwt_payload "$ACCESS_TOKEN"

aws cognito-idp initiate-auth \
    --auth-flow REFRESH_TOKEN_AUTH \
    --client-id "$CLIENT_ID" \
    --auth-parameters REFRESH_TOKEN="$REFRESH_TOKEN"

TOKEN="$ACCESS_TOKEN" python - << 'PY'
import base64
import datetime
import json
import os

token = os.environ["TOKEN"]
parts = token.split(".")

if len(parts) != 3:
    raise SystemExit("Invalid JWT: expected three dot-separated segments")

payload = parts[1]
payload += "=" * (-len(payload) % 4)

decoded = base64.urlsafe_b64decode(payload)
claims = json.loads(decoded)
for name in ("iat", "exp"):
    timestamp = claims[name]
    value = datetime.datetime.fromtimestamp(
        timestamp,
        tz=datetime.UTC,
    )
    print(f"{name}: {value.isoformat()}")
PY
