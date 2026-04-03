# Sanitization and scope notes

This repository is a curated publication snapshot, not a byte-for-byte mirror of the original private research directories.

## Sanitization

To make the artifact archive safe to publish while preserving meaning, environment-specific references were replaced with placeholders in copied text files. Examples include:

- private home-directory paths,
- depot storage roots,
- named HPC hosts,
- machine-specific execution paths.

Typical placeholders include:

- `<FRESCO_DATA_ROOT>`
- `<FRESCO_ARCHIVE_ROOT>`
- `<FRESCO_V3_CODE_ROOT>`
- `<FRESCO_V4_CODE_ROOT>`
- `<REDACTED_HPC_HOST>`
- `<REDACTED_COMPUTE_HOST>`

These substitutions were made only to copied text artifacts in this public snapshot.

## Scope decisions

Included:

- paper materials,
- documentation and runbooks,
- configs and scripts,
- lightweight experiment records,
- compact historical notes that help explain the research path.

Excluded:

- raw datasets,
- large parquet outputs and matched-index binaries,
- bulky intermediate artifacts from the older `FRESCO-Research` workspace,
- internal workflow scaffolding that does not materially help a reader understand or audit the paper.

## Canonicality

For the paper’s final claims, treat the following as canonical:

- `paper/EXP-085-Results.md`
- `fresco-v3/docs/WORKLOAD_TAXONOMY_AND_MATCHING.md`
- `fresco-v3/docs/SCHEMA_AND_PROVENANCE.md`
- `fresco-v3/docs/MASTER_INDEX.md`
- the corresponding copied `fresco-v3` and `fresco-v4` experiment records

The `historical-notes/` tree is intentionally preserved as context, but it should not override the canonical v3/v4 documentation.
