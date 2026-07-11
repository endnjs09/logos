# Schemas

Schemas define the contracts for configuration, harness assets, benchmark tasks,
run artifacts, measurement logs, and comparison reports.

The harness should treat these schemas as public contracts. Runtime code may
evolve, but schema changes should be deliberate and documented.

Important schema families:

- `target-manifest.schema.json`: supported CLI installation target contract.
- `plugin-manifest.schema.json`: external harness pack contract.
- `benchmark-*.schema.json`: repeatable experiment input contracts.
- `measurement-log.schema.json`: calibration measurement contract.
