---
name: search-aws-docs
description: Understand AWS services and find API references by querying official documentation. Use whenever the user asks how something works, wants API references or code-relevant parameter/signature details, needs configuration options, limits, quotas, regional availability, or best practices for any AWS service (EC2, S3, Lambda, EKS, IAM, etc.)—even if they don't mention "docs." Covers both conceptual understanding and code-adjacent lookups (there is no separate AWS code-reference skill).
context: fork
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws)
---

# AWS Docs

## Tools

| Tool | Use For |
|------|---------|
| `aws___search_documentation` | Find documentation—concepts, guides, API references, configuration |
| `aws___read_documentation` | Get full page content (when search excerpts aren't enough) |
| `aws___recommend` | Discover related docs and best practices |
| `aws___get_regional_availability` | Check service/feature availability per region |
| `aws___list_regions` | List all AWS regions |

## When to Use

- **Understanding concepts** — "How does S3 bucket versioning work?"
- **API references** — "RunInstances parameters", "PutBucketEncryption"
- **Configuration options** — "EKS node group settings"
- **Limits & quotas** — "Lambda concurrency limits", "EBS volume limits"
- **Regional availability** — "Is Graviton supported in me-central-1?"
- **Best practices** — "IAM least privilege", "KMS key rotation"

## Query Effectiveness

Good queries are specific:

```
# ❌ Too broad
"Lambda"

# ✅ Specific
"Lambda Python runtime environment variables"
"S3 SSE-KMS bucket policy cross-account"
"EKS pod security admission controller"
```

Include context:
- **Service + feature** when relevant (`EC2 Nitro Enclaves`, `EBS gp3`)
- **Task intent** (`API reference`, `best practices`, `troubleshooting`)
- **SDK version** for code-related queries (`AWS SDK for Python v3`)

## When to Read Full Page

Read after search when:
- **API references** — need complete parameter lists
- **Tutorials** — need full step-by-step instructions
- **IAM policies** — need exact permission statements
- **Search excerpt is cut off** — full context needed

## When to Check Regional Availability

Check before recommending services when:
- Deploying to newer or opt-in regions
- Using recently launched features
- User asks about specific region support

## Why Use This

- **Accuracy** — live docs, not training data that may be outdated
- **Completeness** — API refs have all parameters, not fragments
- **Authority** — official AWS documentation
