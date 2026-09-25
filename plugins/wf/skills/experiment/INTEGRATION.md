# Integration Experiment

Use when the experiment crosses a real external boundary: SDKs, REST APIs, cloud APIs/resources, message brokers, databases, and external/internal services. Apply alongside [RUNTIME.md](RUNTIME.md) when a minimal app, test host, container, or process provides the executable harness.

## Select the smallest tool

- REST/API behavior -> `curl`, `Invoke-RestMethod`, or `Invoke-WebRequest`; use a script when multiple/repeated steps are required.
- AWS resource/API behavior -> check `aws --version`; prefer AWS CLI when it directly answers the question.
- Azure resource/API behavior -> check `az version`; prefer Azure CLI when it directly answers the question.
- SDK-specific behavior -> existing integration-test project and real SDK.
- Broker/distributed behavior -> smallest producer/consumer/app set using the repo's stack.
- Database behavior -> existing data-access stack against local/scratch data.
- Cross-component behavior -> reuse the entry-point/gateway integration-test or runtime setup.

## Cloud

1. Inspect existing AWS/Azure CLI, SDK, IaC, profile/subscription, and environment conventions.
2. If CLI is available, verify the active identity/account/subscription before resource operations.
3. Do not install CLIs, log in, create credentials, or reconfigure accounts solely for the experiment.
4. Use CLI for cloud service/API/resource truth.
5. Use SDK tests for SDK serialization, exceptions, pagination, retries, or client-specific behavior.
6. Filter CLI output to the fields that answer the question.
7. Use only local/sandbox/experiment resources for mutations; clean them up when finished.

## SDK / integration test

1. Reuse existing integration-test projects, fixtures, clients, and test bases.
2. Prefer a sibling integration test for one component; use the existing cross-component/gateway integration-test area for multi-component questions.
3. Exercise the real SDK/boundary; do not stub the dependency under investigation.
4. Assert the actual response, error, limit, pagination, or state transition being validated.

## Brokers and multi-app flows

1. Reuse the repository's broker/client libraries and container/runtime setup.
2. Create only the processes needed to expose the behavior.
3. Make producer, consumer, acknowledgement/retry state, and observed messages visible.
4. Use local or sandbox broker resources.
5. Prefer Compose or the repo's existing orchestration only when multiple processes/resources require it.

## Result

Record the command/run path, observed result, and answered question. Preserve useful assertions/contract knowledge in production code; keep experiment artifacts throwaway.
