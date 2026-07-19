# Learn Hub API

Learn Hub is a serverless course API built with Python, AWS SAM, API Gateway,
Lambda, and DynamoDB. Request validation uses Pydantic and project dependencies
are managed with uv.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Return the service status and application version. |
| `POST` | `/courses` | Validate and create a course. |

Example course request:

```json
{
  "title": "AWS Cloud Fundamentals",
  "description": "Learn the foundations of AWS.",
  "difficulty": "beginner",
  "tags": ["aws", "cloud"]
}
```

`difficulty` must be `beginner`, `intermediate`, or `advanced`. The `tags`
field is optional and defaults to an independent empty list for each request.
Unknown request fields and blank titles, descriptions, or tags are rejected.

A successful request returns `201`. Validation failures return `422`, and a
course whose normalized slug already exists returns `409`.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- AWS SAM CLI
- Docker for `sam local` and container builds
- AWS CLI credentials for deployment or access to a deployed DynamoDB table

## Setup

Install the locked application and development dependencies:

```bash
uv sync
```

Run Python commands through `uv run`; plain `python` may use a different
interpreter that cannot see the uv environment.

SAM installs Lambda dependencies from `src/requirements.txt`, not from the
local `.venv`. Regenerate that file whenever production dependencies change:

```bash
uv export \
  --format requirements-txt \
  --no-dev \
  --no-emit-project \
  --output-file src/requirements.txt
```

## Tests and linting

Unit tests mirror the application packages:

```text
tests/unit/
├── core/
├── handlers/
├── repositories/
├── schemas/
└── services/
```

Run the current application unit suites:

```bash
PYTHONPATH=src uv run python -m pytest \
  tests/unit/core \
  tests/unit/repositories \
  tests/unit/schemas \
  tests/unit/services \
  tests/unit/handlers/test_health.py \
  -v
```

The repository and service tests use mocks or an in-memory fake and do not
contact AWS.

Run Ruff:

```bash
uv run ruff check src tests
```

## Build

Build both Lambda functions and package the dependencies from
`src/requirements.txt`:

```bash
sam build
```

The build artifacts are written to `.aws-sam/build`.

## Local API

The SAM template's `!Ref LearnHubTable` is not resolved to a deployed physical
table name during every local workflow. `sam local` also does not create a
DynamoDB table; it calls DynamoDB using the active AWS credentials and region.

After deploying the stack, retrieve the physical table name:

```bash
aws cloudformation describe-stack-resource \
  --stack-name learn-hub-app \
  --logical-resource-id LearnHubTable \
  --region us-east-1
```

Create an uncommitted `env.local.json` using the returned
`PhysicalResourceId`:

```json
{
  "CoursesFunction": {
    "TABLE_NAME": "learnhub-learn-hub-app"
  }
}
```

Then start the API:

```bash
sam build
sam local start-api --env-vars env.local.json
```

Example requests:

```bash
curl http://127.0.0.1:3000/health

curl --request POST http://127.0.0.1:3000/courses \
  --header 'Content-Type: application/json' \
  --data '{
    "title": "AWS Cloud Fundamentals",
    "description": "Learn the foundations of AWS.",
    "difficulty": "beginner",
    "tags": ["aws", "cloud"]
  }'
```

## Deploy

The default stack name in `samconfig.toml` is `learn-hub-app`. Deploy to
`us-east-1` with:

```bash
sam build
sam deploy \
  --stack-name learn-hub-app \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM \
  --resolve-s3
```

The deployed Lambda receives the physical DynamoDB table name automatically
through `TABLE_NAME: !Ref LearnHubTable`.

Verify the table after deployment:

```bash
aws dynamodb describe-table \
  --table-name learnhub-learn-hub-app \
  --region us-east-1
```

Remove the deployed stack and its resources when they are no longer needed:

```bash
sam delete --stack-name learn-hub-app --region us-east-1
```

## Project structure

```text
src/
├── core/          # Constants, exceptions, and HTTP response helpers
├── handlers/      # Lambda entry points
├── repositories/  # DynamoDB persistence
├── schemas/       # Pydantic request schemas
├── services/      # Application and domain workflow
├── utils/         # Shared utilities
├── requirements.txt
└── VERSION
```
