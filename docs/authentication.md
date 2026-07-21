# Authentication

Identity Provider

- Cognito

## Cognito Tokens

### ID token

Used by the client to understand the authenticated identity.

Important claims:

- sub
- email
- aud
- token_use=id
- iat
- exp

### Access token

Sent to the learn-hub-app as a bearer token

Important claims:

- sub
- client_id
- scope
- token_use=access
- iat
- exp

### Refresh token

Used to request new short-lived tokens. It is not sent to the learn-hub-app

Identity

- JWT

Stable Identifier

- sub

Application User

- DynamoDB

Authorization

- LearnHub

## LearnHub User

PK = USER#{sub}

SK = PROFILE

Fields

- id
- cognito_sub
- email
- display_name
- role
- status
- avatar_url
- created_at
- updated_at

## Application User Provisioning

Flow:

Cognito Post Confirmation
- Publisher lambda
- EventBridge
- SQS
- Provision user lambda
- DynamoDB

### Domain event

Source: learnhub.identity
Detail type: UserConfirmed

Schema:
- schema_version
- user_sub
- email
- confirmed_at

### Delivery guarantees

The consumer must be idempotent because events may be delivered more than once.

### Failure handling

Failed messages are retried by SQS

Messages that repeatedly fail are moved to dead-letter queue.
