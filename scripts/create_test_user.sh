#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=read_deployed_cognito_identifiers.sh
source "$SCRIPT_DIR/read_deployed_cognito_identifiers.sh"

TEST_EMAIL="${TEST_EMAIL:-oliver@example.com}"
TEST_PASSWORD="${TEST_PASSWORD:-Oliver.test@123}"

aws cognito-idp sign-up \
  --client-id "$CLIENT_ID" \
  --username "$TEST_EMAIL" \
  --password "$TEST_PASSWORD" \
  --user-attributes Name=email,Value="$TEST_EMAIL"

aws cognito-idp admin-confirm-sign-up \
  --user-pool-id "$USER_POOL_ID" \
  --username "$TEST_EMAIL"

aws cognito-idp admin-get-user \
  --user-pool-id "$USER_POOL_ID" \
  --username "$TEST_EMAIL"
