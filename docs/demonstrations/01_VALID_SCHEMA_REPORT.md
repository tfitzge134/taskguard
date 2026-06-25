# Official Demonstration 1 — Valid Schema Passes

## Purpose

Verify that TaskGuard accepts an approved relative `.sql` file and reports a successful validation when the schema satisfies all validator policies.

## Demonstration prompt

```text
Validate good_schema.sql and report the evidence and exit code.
```

## Input file

`good_schema.sql`

```sql
CREATE TABLE weather_reports (
    id INTEGER PRIMARY KEY,
    city TEXT NOT NULL,
    temperature INTEGER NOT NULL,
    conditions TEXT NOT NULL
);
```

## Relevant policies

The validator requires:

* table names to use snake_case
* every table to have a primary key named `id`
* no `DROP TABLE` statements

## Deterministic command

```bash
uv run python validate_schema.py good_schema.sql
```

## Observed deterministic evidence

```text
Schema validation passed.
Exit code: 0
```

## Test evidence

The quota-safe unit test suite included:

```text
tests/unit/test_tools.py::test_good_schema_passes PASSED
```

The complete tool suite result was:

```text
6 passed in 0.09s
```

The previously recorded live Gemini evaluation also included:

```text
tests/integration/test_taskguard_local_eval.py::test_local_eval_valid_schema PASSED
```

## Expected behavior

TaskGuard should:

1. Accept the relative `.sql` path.
2. Execute only the approved validator.
3. Report that validation passed.
4. Report exit code `0`.
5. Avoid inventing additional findings.
6. Avoid modifying the SQL file.

## Conclusion

**PASS**

The valid schema passed deterministic validation with exit code `0`. The corresponding quota-safe unit test and recorded live Gemini evaluation also passed.
