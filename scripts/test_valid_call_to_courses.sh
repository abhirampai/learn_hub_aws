#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=authenticate_user.sh
source "$SCRIPT_DIR/authenticate_user.sh"

if [[ -z "${COURSES_URL:-}" ]]; then
  HEALTH_API_URL=$(get_stack_output HealthApi)
  COURSES_URL="${HEALTH_API_URL%/health/}/courses"
fi

curl \
  --fail-with-body \
  --silent \
  --show-error \
  --request POST \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
    "title": "Learn SAM",
    "description": "Infrastructure as Code",
    "difficulty": "beginner"
  }' \
  "$COURSES_URL"

printf '\n'
