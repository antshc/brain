# Initialize missing docs

Use the docs root supplied by the caller. Check each file independently. Create missing files immediately, using only established context. Preserve existing files byte for byte.

- `ARCHITECTURE.md`: render the bootstrap architecture format with only the system overview and Context. Add optional sections later through **Ensure section exists** when their content exists.
- `GLOSSARY.md`: render the bootstrap glossary format with the context heading and empty Language section. To capture settled terms, *run `record-architecture` skill to persist a settled glossary term* in **term** mode.

Create only these two files. Record owners create `docs/adr/`, `docs/concepts/`, and `docs/building-blocks/` lazily. Done when both files exist under the supplied root and every pre-existing file is unchanged.
