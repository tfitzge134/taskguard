# Official Demonstration 2 — Invalid Schema Reports Complete Evidence

## Purpose

Verify that TaskGuard reports every failure produced by the approved validator and recommends one focused next action without inventing unsupported findings.

## Demonstration prompt

```text
Validate bad_schema.sql. Explain every failure using only the validation evidence and recommend one next step.
```

## Input file

`bad_schema.sql`

```sql
DROP TABLE IF EXISTS legacy_users;

CREATE TABLE userProfile (
    id INT PRIMARY KEY,
    bio TEXT
);

CREATE TABLE posts (
    title TEXT,
    content TEXT,
    created_at TIMESTAMP
);

CREATE TABLE comments (
    id INT PRIMARY KEY,
    post_id INT,
    body TEXT
);
```

## Deterministic command

```bash
uv run python validate_schema.py bad_schema.sql
```

## Observed deterministic evidence

```text
ERROR: 'DROP TABLE' statements are forbidden.
ERROR: Table 'userProfile' must be snake_case.
ERROR: Table 'posts' is missing a primary key named 'id'.
Exit code: 1
```

## Verified validator findings

The validator produced exactly three failures:

1. A forbidden `DROP TABLE` statement is present.
2. The table name `userProfile` is not snake_case.
3. The table `posts` is missing a primary key named `id`.

No failure was reported for the `comments` table because it has an `id` primary key and uses a valid snake_case name.

## Test evidence

The quota-safe unit test suite included:

```text
tests/unit/test_tools.py::test_bad_schema_reports_expected_failures PASSED
```

The complete tool suite result was:

```text
6 passed in 0.09s
```

The previously recorded live Gemini evaluation also included:

```text
tests/integration/test_agent.py::test_taskguard_validates_bad_schema PASSED
tests/integration/test_taskguard_local_eval.py::test_local_eval_invalid_schema PASSED
```

## Expected behavior

TaskGuard should:

1. Accept the approved relative `.sql` path.
2. Run only the approved validator.
3. Report all three validator failures.
4. Report the nonzero exit code.
5. Avoid adding failures not present in the validator evidence.
6. Recommend exactly one focused next action.
7. Avoid automatically modifying the SQL file.

## Focused next action

Correct the three verified policy violations in `bad_schema.sql`, then run validation again.

## Conclusion

**PASS**

The invalid schema produced all three expected failures and exit code `1`. The quota-safe unit test and recorded live Gemini integration and evaluation tests also passed.
