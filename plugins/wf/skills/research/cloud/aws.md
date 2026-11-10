# AWS

Provider reference for an AWS cloud part. Contract: [cloud-inspection.md](cloud-inspection.md).

## Contents

- Docs
- SDK
- AWS CLI
- Gotchas

## Docs

Search and read official AWS documentation — service guides, API references, SDK references, Service Quotas, regional availability. Use the AWS Documentation MCP tools (search, read full page, recommend related, regional availability, list regions) when installed; otherwise fetch `docs.aws.amazon.com` pages directly. Search with service, feature, intent, and resolved SDK version when applicable; read the full page for complete API, policy, or quota details. Verify regional availability before relying on a regional feature.

## SDK

AWS SDK for .NET (`AWSSDK.*`, `AWS.Logger.*`):

1. Resolve the version from the workspace — `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`, `*.csproj`; absent → `obj/project.assets.json`. Never reuse a version from an earlier session.
2. Send an Explore request directly to `hunter` with `@shape: nuget` to verify the type, member, signature, and behavior using the restored package’s XML docs or decompiled assembly. If Hunter is unavailable, report the blocked lookup and continue independent evidence work.
3. Version-specific behavior, release notes, or retry/config defaults not visible in the package → official AWS SDK docs per Docs.

Other SDKs: resolve the version from the dependency manifest and lockfile, then use Docs.

## AWS CLI

Read-only research of the live account. Check `command -v aws`; absent → UNKNOWN per Probes.

1. **Identity** — `aws sts get-caller-identity`; record account and principal ARN.
2. **Pin** — pass `--region` and `--profile` (when set) on every call; never rely on an implicit default.
3. **Discover** — `aws <service> help` or `aws <service> <command> help` for unfamiliar commands or flags.
4. **Read** — only `describe-*`, `list-*`, `get-*`, plus:

| Need | Command |
|---|---|
| Applied quota | `aws service-quotas get-service-quota --service-code <code> --quota-code <code>` |
| Default quota | `aws service-quotas get-aws-default-service-quota --service-code <code> --quota-code <code>` |
| Quota codes | `aws service-quotas list-service-quotas --service-code <code>` |
| Service codes | `aws service-quotas list-services` |
| Effective permissions | `aws iam simulate-principal-policy --policy-source-arn <arn> --action-names <action> [--resource-arns <arn>]` |
| Resource state | `aws <service> describe-*` / `list-*` / `get-*` |
| Request validation | `--dry-run` on EC2 calls that support it |

5. **Shape output** — `--output json --query '<JMESPath>'` to extract the cited field.

**MUST NOT** run create, put, update, modify, delete, attach, tag, or any other mutating command.

## Gotchas

**Service Quotas default ≠ applied.** `get-aws-default-service-quota` returns the documented default; `get-service-quota` returns the account's applied value — some quotas are not tracked and return only a default.

**Quotas and features are regional.** A value read in one region says nothing about another; record the region for every quota and availability claim.

**`simulate-principal-policy` ignores some policy types.** SCPs and resource policies may not be evaluated unless supplied; record what the simulation covered.
