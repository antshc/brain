# AWS

Web provider resource. Apply the Brief, including Provider only.

- **Docs** — AWS documentation tools or the official AWS docs site: service guides, API and SDK references, Service Quotas, regional availability. Confirm a feature is available in the target region before relying on it.
- **SDK** — AWS SDK for .NET (`AWSSDK.*`, `AWS.Logger.*`): verify type, member, signature, and behavior from the restored package per the SDK rule.
- **Live account** — the AWS CLI. Discover through help: the caller identity (account, principal ARN); the Service Quotas service for applied vs default values and the service and quota codes to query them; IAM policy simulation for effective permissions; each service's describe/list/get operations for resource state; dry-run where the service supports it. Pin region and profile.
- **Gotchas** — The default-quota lookup returns the documented default, the applied-quota lookup the account's value; some quotas are untracked and return only a default. Quotas and features are regional; record the region for every such claim. Policy simulation may skip SCPs and resource policies unless supplied; record what it covered.
