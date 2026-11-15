# Initialize missing docs

## Inputs

Caller docs root and established system/glossary context.

## Check each file

Run only when requested. Use the caller's docs root; for a direct request use the established repository docs root or ask if unclear. Check each file independently, create missing files immediately using established context, and preserve existing files byte for byte.

## Create missing docs

- ARCHITECTURE.md: render only the system overview and Context from the architecture bootstrap. Add optional sections later through Ensure section exists when content exists.
- GLOSSARY.md: render the glossary bootstrap's context heading and empty Language section. Settled terms require the separate `term` route.

Create only these two files. Record routes create docs/adr/, docs/concepts/, and docs/building-blocks/ lazily.

## Completion criteria

Both files exist under the supplied root; every pre-existing file is unchanged.
