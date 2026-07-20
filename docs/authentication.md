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
