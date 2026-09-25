# Experiment examples

Example prompts that should trigger an experiment when the answer requires observing real behavior.

## Logic / state

- Test whether this state machine can move from `Failed` directly to `Running`.
- Verify how the reducer behaves when the same event is applied twice.
- Can we prove this retry-state logic handles an expired operation correctly?

## UI / frontend

- Try three layouts for this settings page and see which interaction works.
- Prototype alternative ways to show validation errors in this React form.
- Test how this table feels with realistic data density and long values.

## REST API / service integration

- Test if the Keycloak client supports `viewer` permission.
- Verify what this endpoint actually returns when the token is expired.
- Let's try the API with an invalid continuation token and inspect the response.

## SDK

- Test whether the AWS SDK paginator repeats items when the token changes.
- Verify which exception the Keycloak client returns for an unauthorized request.
- Check the actual SDK response when the resource does not exist.

## Cloud resource / API

- Test whether this IAM role can assume the target role with the current trust policy.
- Verify if Azure accepts this configuration on a scratch resource.
- Let's check how AWS behaves when the snapshot limit is reached.

## Message broker

- Test whether Service Bus redelivers the message after the consumer crashes before acknowledgement.
- Verify how duplicate messages behave with the current consumer setup.
- Build the smallest producer/consumer flow to check retry and dead-letter behavior.

## Database

- Test whether this query uses the expected index with realistic data.
- Verify how the database handles two concurrent updates to the same row.
- Check the actual persisted values after this transaction rolls back.

## Runtime / framework

- Test whether ASP.NET Core disposes this scoped service when the request is cancelled.
- Verify how the serializer handles this polymorphic payload.
- Can we prove this background service shuts down within the configured timeout?

## Cross-component integration

- Test whether the gateway forwards the Keycloak role claim unchanged to the downstream API.
- Verify the real flow from API request through broker to consumer.
- Let's check whether these two services agree on the error contract.
