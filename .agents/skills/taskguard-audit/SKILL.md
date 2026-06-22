---
name: taskguard-audit
description: Audit TaskGuard using evidence-first debugging, automated tests, and security checks without modifying files unless the user approves.
---

# TaskGuard Audit Skill

Use this skill when reviewing TaskGuard code, tests, security controls, or capstone readiness.

## Required workflow

Follow this sequence:

1. Audit
2. Investigate
3. Test
4. Implement only after approval

Do not treat an inference as proof.

## Audit procedure

1. Inspect only the project files relevant to the review.
2. Check the current Git status.
3. Run the narrowest relevant tests first.
4. Read the complete test and error output.
5. Separate confirmed findings from unverified concerns.
6. Recommend one focused next action.
7. Do not modify files without explicit user approval.

## Security checks

Verify that TaskGuard:

- rejects absolute paths
- rejects directory traversal such as `../`
- accepts only approved file types
- does not execute arbitrary shell commands
- records command output and exit codes
- does not expose credentials or environment variables
- does not modify files without approval

Do not open or print:

- `.env` files
- API keys
- Google authentication files
- credential files
- private keys

## Approved test command

```bash
uv run pytest tests/unit/test_tools.py -v
```

## Required audit report

Return the following sections.

### Tests executed

List the exact commands that were run.

### Evidence

Report actual test output, exit codes, and relevant file locations.

### Confirmed findings

Include only findings supported by inspected code or test results.

### Unverified concerns

Clearly label anything that has not been tested.

### Recommended next step

Recommend one focused action.

### Files modified

The default response must be:

`No files modified.`
