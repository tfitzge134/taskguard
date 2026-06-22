# TaskGuard Project Log

## Project

- **Name:** TaskGuard
- **Track:** Agents for Business
- **Repository:** https://github.com/tfitzge134/taskguard
- **Local project:** `/Users/teresafitzgerald/agy2-projects/my-agent`

## Development method

TaskGuard follows:

> Audit → Investigate → Test → Implement

An inference is not treated as proof. Important conclusions must be supported by inspected code, command output, logs, or automated tests.

---

## 2026-06-22 — Project initialization

### Capstone decision

Selected TaskGuard as the capstone project.

TaskGuard is an evidence-based Google ADK agent that:

1. Receives a validation request.
2. Calls an approved validation tool.
3. Captures actual output and exit codes.
4. Explains failures using returned evidence.
5. Recommends one focused next action.
6. Rejects unsafe requests.
7. Does not modify files without approval.

### Competition track

Selected:

**Agents for Business**

TaskGuard solves a software-development and validation workflow problem.

### Scope decision

The first version will not require:

- cloud deployment
- a frontend
- RAG
- a database
- unrestricted shell execution
- automatic file modification
- a large multi-agent architecture

---

## Baseline audit

### Existing files identified

Important existing project files included:

- `app/agent.py`
- `validate_schema.py`
- `good_schema.sql`
- `bad_schema.sql`
- `tests/`
- `pyproject.toml`
- `uv.lock`

### Starter agent

The original Google ADK starter agent provided simulated weather and time tools.

### Decision

Replace the starter behavior with TaskGuard while preserving the working ADK application structure.

---

## Schema validator verification

### Valid schema test

Command:

```bash
python3 validate_schema.py good_schema.sql
echo "Exit code: $?"
```

Result:

```text
Schema validation passed.
Exit code: 0
```

Conclusion:

The validator correctly accepts the valid schema.

### Invalid schema test

Command:

```bash
python3 validate_schema.py bad_schema.sql
echo "Exit code: $?"
```

Result:

```text
ERROR: 'DROP TABLE' statements are forbidden.
ERROR: Table 'userProfile' must be snake_case.
ERROR: Table 'posts' is missing a primary key named 'id'.
Exit code: 1
```

Conclusion:

The validator correctly detects all three intended policy violations.

---

## Git and GitHub setup

### Repository isolation

The original parent Git repository was rooted at:

```text
/Users/teresafitzgerald
```

A dedicated Git repository was created at:

```text
/Users/teresafitzgerald/agy2-projects/my-agent
```

### GitHub repository

The project was pushed to:

```text
https://github.com/tfitzge134/taskguard
```

### Repository safety

The `.gitignore` excludes:

- virtual environments
- Python caches
- environment-variable files
- credentials and private keys
- local ADK runtime state
- backup files
- generated deployment metadata

Local generated files removed from Git tracking:

- `app/.adk/session.db`
- `app/agent.py.save`

---

## Safe validation tool

Created:

```text
app/tools.py
```

Implemented:

```text
run_schema_validation
```

The tool:

- accepts relative `.sql` paths
- rejects absolute paths
- rejects directory traversal
- rejects non-SQL files
- rejects missing files
- runs only the approved validator
- captures standard output
- captures standard error
- captures the exit code
- reports whether a file was modified
- does not execute arbitrary user-provided shell commands

### Direct tool tests

Verified:

| Input | Expected | Actual |
|---|---|---|
| `good_schema.sql` | passed | passed |
| `bad_schema.sql` | failed | failed |
| `../bad_schema.sql` | rejected | rejected |

Security evidence:

```text
Directory traversal is not allowed.
```

---

## Automated unit tests

Created:

```text
tests/unit/test_tools.py
```

Test command:

```bash
uv run pytest tests/unit/test_tools.py -v
```

Result:

```text
3 passed in 0.09s
```

Tests cover:

- valid schema acceptance
- invalid schema evidence
- directory-traversal rejection

---

## Authentication investigation

### Vertex AI investigation

The Google Cloud CLI initially had:

- no active account
- no selected project

After authentication, all available Google Cloud projects were checked.

Result:

```text
billingEnabled=False
```

for every available project.

### Decision

Do not enable Google Cloud billing merely to run this local capstone.

### Selected authentication method

TaskGuard uses Google AI Studio through environment variables:

```text
GEMINI_API_KEY
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

The API key is not stored in project source code or committed to Git.

---

## TaskGuard ADK agent

Converted:

```text
app/agent.py
```

The agent now:

- uses Google ADK
- uses `gemini-2.5-flash`
- calls `run_schema_validation`
- follows evidence-first debugging
- distinguishes passed, failed, rejected, and error results
- reports exit codes when available
- does not modify files
- does not execute arbitrary shell commands

### Application load test

Result:

```text
App name:    taskguard
Agent name:  taskguard_agent
Tool count:  1
Tool name:   run_schema_validation
TaskGuard loaded successfully.
```

---

## End-to-end ADK tests

### Invalid schema test

Request:

```text
Validate bad_schema.sql. Explain every failure using only the validation evidence and recommend one next step.
```

Verified behavior:

- status reported as `failed`
- exit code `1` reported
- forbidden `DROP TABLE` reported
- invalid `userProfile` table name reported
- missing `id` primary key in `posts` reported
- one focused next step recommended
- no file modified

### Valid schema test

Request:

```text
Validate good_schema.sql and report the evidence and exit code.
```

Result:

```text
Status: passed
Evidence: Schema validation passed.
Exit code: 0
```

Conclusion:

The complete ADK agent correctly handles a passing validation.

### Unsafe-path security test

Request:

```text
Validate ../bad_schema.sql and explain whether any command was executed.
```

Result:

```text
Status: rejected
Evidence: Directory traversal is not allowed.
No validation command was executed.
```

Conclusion:

Directory traversal is blocked through both the deterministic tool and the complete ADK agent workflow.

---

## Course concepts demonstrated

### Completed

- [x] Google ADK agent
- [x] Custom deterministic function tool
- [x] Security controls
- [x] Automated testing
- [x] Evidence-based evaluation
- [x] Git and GitHub production workflow

### Planned

- [ ] TaskGuard Agent Skill
- [ ] Bounded Antigravity audit
- [ ] Expanded evaluation report
- [ ] Architecture diagram
- [ ] Final public README
- [ ] Five-minute demonstration video
- [ ] Kaggle Writeup
- [ ] Final Kaggle submission

---

## Current working status

Confirmed working:

- safe schema-validation tool
- valid-schema workflow
- invalid-schema workflow
- directory-traversal protection
- Google ADK agent integration
- Gemini API authentication
- three automated unit tests
- public GitHub repository

## Current next step

Create and verify:

```text
.agents/skills/taskguard-audit/SKILL.md
```

Then open TaskGuard in Antigravity and perform a bounded audit that:

1. inspects the specification and relevant files
2. runs the existing tests
3. checks security controls
4. produces an evidence-based gap report
5. does not modify files without approval
