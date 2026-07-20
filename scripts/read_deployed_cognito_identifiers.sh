#!/usr/bin/env bash

set -euo pipefail

STACK_NAME="${STACK_NAME:-learn-hub-app}"

get_stack_output() {
  local output_key="$1"
  local value

  value=$(
    aws cloudformation describe-stacks \
      --stack-name "$STACK_NAME" \
      --query "Stacks[0].Outputs[?OutputKey=='${output_key}'].OutputValue | [0]" \
      --output text
  )

  if [[ -z "$value" || "$value" == "None" ]]; then
    printf 'CloudFormation output %s was not found in stack %s.\n' "$output_key" "$STACK_NAME" >&2
    return 1
  fi

  printf '%s\n' "$value"
}

USER_POOL_ID=$(get_stack_output LearnHubUserPoolId)
CLIENT_ID=$(get_stack_output LearnHubUserPoolClientId)

printf 'USER_POOL_ID=%s\n' "$USER_POOL_ID"
printf 'CLIENT_ID=%s\n' "$CLIENT_ID"
