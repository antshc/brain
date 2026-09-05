---
name: query-azure
description: Discover, inspect, create, update, and delete real Azure resources with Azure CLI. Use whenever the user asks to list, show, provision, change, or remove Azure resources with `az`, even if they do not explicitly ask for this skill.
compatibility: Requires Azure CLI (`az`) to be installed and authenticated with access to the target Azure subscription.
---

# Azure CLI Operations

## Resource Operations

1. Resolve the resource type, resource name, resource group, location, subscription, and service-specific inputs required by the request. Ask only for values that cannot be discovered or safely inferred.
2. For unfamiliar commands or flags, run `az <group> <command> --help`. For service behavior, limits, or current guidance: Run `/azure-platform:ms-docs` skill.
3. Run read and discovery commands directly.
4. Run requested create and update commands directly once all required inputs and the target subscription are resolved. Do not add a confirmation step.
5. Validate each create or update with the narrowest matching `show` or `list` command and report the resulting resource ID and subscription without exposing credentials.

Prefer service-specific commands such as `az group`, `az storage account`, or `az webapp` over generic `az resource` commands when Azure CLI provides them.

## Delete Gate

1. Resolve the exact resource type, name or resource ID, resource group, and subscription.
2. Show the full deletion target to the user and ask for explicit confirmation immediately before running the delete command.
3. Do not infer confirmation from an earlier request, accept ambiguous confirmation, widen the target, or delete multiple resources unless every target was shown and confirmed.
4. After confirmation, run the narrowest service-specific delete command.
5. Verify absence with the matching `show` or `list` command and report the result.