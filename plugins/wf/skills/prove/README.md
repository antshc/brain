# Prove examples

Example prompts that should trigger Prove when the answer requires executing a check against the actual mechanism, grouped by route.

Source-only requests such as "find the guard that prevents this transition", "trace this retry flow", or "analyze this IAM policy" belong to Research. Writing a test or prototype without running it does not complete Prove.

## Logic

- Test whether this state machine can move from `Failed` directly to `Running`.
- Verify how the reducer behaves when the same event is applied twice.
- Can we prove this retry-state logic handles an expired operation correctly?

## UI

- Run a browser E2E check that submitting an invalid form shows the field error and sends no request.
- Test that keyboard focus returns to the triggering button after this dialog closes.
- Run this table at a narrow viewport with long values and assert that its actions remain reachable.

## Runtime

- Test whether ASP.NET Core disposes this scoped service when the request is cancelled.
- Verify how the serializer handles this polymorphic payload.
- Can we prove this background service shuts down within the configured timeout?

## Integration

### REST API / service

- Test if the Keycloak client supports `viewer` permission.
- Verify what this endpoint actually returns when the token is expired.
- Let's try the API with an invalid continuation token and inspect the response.

### SDK

- Test whether the AWS SDK paginator repeats items when the token changes.
- Verify which exception the Keycloak client returns for an unauthorized request.
- Check the actual SDK response when the resource does not exist.

### Cloud resource / API

- Test whether this IAM role can assume the target role with the current trust policy.
- Verify if Azure accepts this configuration on a scratch resource.
- Let's check how AWS behaves when the snapshot limit is reached.

### Message broker

- Test whether Service Bus redelivers the message after the consumer crashes before acknowledgement.
- Verify how duplicate messages behave with the current consumer setup.
- Build the smallest producer/consumer flow to check retry and dead-letter behavior.

### Database

- Test whether this query uses the expected index with realistic data.
- Verify how the database handles two concurrent updates to the same row.
- Check the actual persisted values after this transaction rolls back.

### Cross-component

- Test whether the gateway forwards the Keycloak role claim unchanged to the downstream API.
- Verify the real flow from API request through broker to consumer.
- Let's check whether these two services agree on the error contract.
