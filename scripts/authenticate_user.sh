#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=read_deployed_cognito_identifiers.sh
source "$SCRIPT_DIR/read_deployed_cognito_identifiers.sh"

TEST_EMAIL="${TEST_EMAIL:-oliver@example.com}"
TEST_PASSWORD="${TEST_PASSWORD:-Oliver.test@123}"

AUTH_RESULT=$(
  aws cognito-idp initiate-auth \
    --auth-flow USER_PASSWORD_AUTH \
    --client-id "$CLIENT_ID" \
    --auth-parameters "USERNAME=$TEST_EMAIL,PASSWORD=$TEST_PASSWORD" \
    --query 'AuthenticationResult.[AccessToken,IdToken,RefreshToken]' \
    --output text
)

IFS=$'\t' read -r ACCESS_TOKEN ID_TOKEN REFRESH_TOKEN <<< "$AUTH_RESULT"

if [[ -z "$ACCESS_TOKEN" || -z "$ID_TOKEN" || -z "$REFRESH_TOKEN" ]]; then
  printf 'Cognito authentication did not return all expected tokens.\n' >&2
  exit 1
fi

printf 'ACCESS_TOKEN_LENGTH=%s\n' "${#ACCESS_TOKEN}"
printf 'ID_TOKEN_LENGTH=%s\n' "${#ID_TOKEN}"
printf 'REFRESH_TOKEN_LENGTH=%s\n' "${#REFRESH_TOKEN}"
