# Experiment Registry Schema

`research/experiments/registry.yaml` holds a list under `experiments:`. Entries are added only after owner
approval following the Phase 17 (or a later) Astra × Fable review. Enforced by `tests/test_experiment_registry.py`.

| Field | Type | Rules |
|---|---|---|
| `experiment_id` | string | `EXP-###`, unique, never reused |
| `title` | string | |
| `proposed_by` | string | e.g. `Fable`, `Owner` |
| `reviewed_by` | list[string] | must include `Astra` |
| `status` | enum | `REGISTERED` → `RUNNING` → `COMPLETED` / `ABANDONED` / `SUPERSEDED` |
| `hypothesis` | string | falsifiable statement |
| `economic_rationale` | string | why the market would behave this way |
| `classification` | enum | `CANON-ABLATION` (tests a canonical optional rule) or `RESEARCH-DERIVED` |
| `variables` | list | each `{name, classification, definition}`; research-derived variables must say `RESEARCH-DERIVED` |
| `parameter_ranges` | mapping | fixed before execution |
| `baseline_comparison` | string | frozen baseline id + hash it is compared against |
| `primary_metric` | string | one metric, e.g. expectancy (R) after costs |
| `secondary_metrics` | list[string] | |
| `development_period` | string | inside 2018-01-01 → 2022-12-31 |
| `validation_period` | string | inside 2023-01-01 → 2024-12-31 |
| `holdout_status` | enum | `LOCKED` for every experiment |
| `failure_condition` | string | stated before running |
| `promotion_condition` | string | stated before running |
| `overfitting_risk` | string | Astra's assessment and constraints |
| `implementation_notes` | string | |
| `astra_ruling` | enum | `APPROVE` / `APPROVE WITH CONSTRAINTS` |
| `owner_approval` | string | reference to the approval report entry |
| `spec_hash` | string | sha256 of the entry (excluding status/result fields), written when status → `RUNNING` |

**Immutability:** once `status` is `RUNNING` or later, every field except `status`, `result_ref` and `closed_note` is
frozen. The test recomputes `spec_hash` and fails on any change. A changed idea gets a new `experiment_id`.
