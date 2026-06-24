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

---

## 2026-06-22 — Antigravity security audit

Antigravity used the `taskguard-audit` Agent Skill to inspect the repository.

### Audit command

```bash
uv run pytest tests/unit/test_tools.py -v
```

### Initial audit result

- All three existing tests passed.
- Git reported a clean working tree.
- No files were modified by Antigravity.
- The existing security implementation was confirmed.
- Antigravity identified three missing test cases:
  - absolute-path rejection
  - non-SQL-file rejection
  - missing-SQL-file rejection

### Confirmed implementation findings

Antigravity confirmed that TaskGuard:

- rejects absolute paths
- rejects directory traversal such as `../`
- accepts only `.sql` files
- uses `subprocess.run` without shell execution
- captures validation output and exit codes
- reports `file_modified` as false
- reads schema files without modifying them

### Action taken

Three focused unit tests were added to:

```text
tests/unit/test_tools.py
```

No change was made to the working implementation in:

```text
app/tools.py
```

### Final verification command

```bash
uv run pytest tests/unit/test_tools.py -v
```

### Final verification result

```text
6 passed in 0.09s
```

The test suite now covers:

1. valid schema acceptance
2. invalid schema evidence
3. directory-traversal rejection
4. absolute-path rejection
5. non-SQL-file rejection
6. nonexistent-SQL-file rejection

### Files modified

- `tests/unit/test_tools.py`
- `PROJECT_LOG.md`

### Audit conclusion

The Antigravity audit identified test-coverage gaps rather than implementation failures. The gaps were resolved by adding focused tests, and all six tests passed.

---

## 2026-06-23 — Integration and full-suite verification

### TaskGuard end-to-end integration test

Updated:

```text
tests/integration/test_agent.py
```

The integration test uses the Google ADK Runner and verifies that TaskGuard:

- receives a request to validate `bad_schema.sql`
- calls `run_schema_validation`
- reports the validation status as failed
- reports exit code `1`
- explains the forbidden `DROP TABLE`
- identifies `userProfile` as not snake_case
- identifies the missing `id` primary key in `posts`
- bases its response on actual tool evidence

Verification result:

```text
1 passed, 7 warnings in 3.96s
```

Git checkpoint:

```text
5a0710c Add TaskGuard end-to-end integration test
```

### Optional Vertex AI runtime tests

The starter repository includes:

```text
app/agent_runtime_app.py
tests/integration/test_agent_runtime_app.py
```

These files support optional Vertex AI Agent Engine deployment.

The runtime requires:

- a configured Google Cloud project
- Vertex AI authentication
- Cloud Logging
- a billing-enabled project

TaskGuard currently uses Google AI Studio locally with:

```text
GEMINI_API_KEY
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

The Vertex runtime tests are skipped unless this variable is explicitly enabled:

```text
RUN_VERTEX_RUNTIME_TESTS=TRUE
```

This keeps optional cloud deployment separate from the local TaskGuard MVP.

Git checkpoint:

```text
6886edb Skip optional Vertex runtime tests without cloud project
```

### Complete test-suite verification

Command:

```bash
uv run pytest \
  tests/unit/test_tools.py \
  tests/integration/test_agent.py \
  tests/integration/test_agent_runtime_app.py \
  -v
```

Result:

```text
7 passed, 1 skipped, 7 warnings in 4.15s
```

The seven passing tests consist of:

- six deterministic validation and security unit tests
- one complete Google ADK and Gemini integration test

The skipped module contains the optional Vertex AI Agent Engine runtime tests.

The warnings originate from Google ADK and Google GenAI dependency features and deprecations. They did not cause test failures.

### Current verified status

Confirmed working:

- safe deterministic schema-validation tool
- valid-schema workflow
- invalid-schema workflow
- directory-traversal rejection
- absolute-path rejection
- non-SQL-file rejection
- missing-file rejection
- complete ADK tool invocation
- evidence-based failure explanation
- Google AI Studio authentication
- bounded Agent Skill audit
- seven passing automated tests
- optional cloud runtime isolated from the local MVP
- clean GitHub checkpoints


---

## 2026-06-24 — Local TaskGuard evaluation

### Evaluation dataset

Replaced the original greeting and weather evaluation cases with five TaskGuard scenarios:

1. valid schema acceptance
2. invalid schema evidence
3. directory-traversal rejection
4. non-SQL-file rejection
5. missing-schema rejection

Dataset:

tests/eval/datasets/basic-dataset.json

### TaskGuard-specific rubric

Updated:

tests/eval/eval_config.yaml

The rubric evaluates:

- required use of run_schema_validation
- evidence grounded in the tool trace
- correct passed, failed, rejected, or error status
- exit-code reporting
- complete invalid-schema findings
- safe handling of rejected requests
- absence of unsupported file-modification claims
- one focused remediation step when needed

### Cloud evaluator investigation

agents-cli versions 0.5.0 and 0.5.1 were inspected.

The eval generate command unconditionally requires a Google Cloud project and runs inference through vertexai.Client and the Vertex AI evaluation service.

Because the TaskGuard MVP uses Google AI Studio and no billing-enabled Google Cloud project, the cloud evaluator was not used. A random project ID was not supplied merely to bypass project detection.

### Local ADK evaluation

Created:

tests/integration/test_taskguard_local_eval.py

The evaluation uses the same Google ADK Runner as the verified integration test and loads prompts directly from the TaskGuard evaluation dataset.

The test suite includes:

- one dataset-structure test
- five live TaskGuard evaluation cases

### Free-tier rate-limit investigation

The first evaluation run completed all assertions but produced a background 429 quota warning. The Google AI Studio free tier reported a limit of five gemini-2.5-flash requests per minute.

A 30-second interval was added between live evaluation cases, and unhandled thread exceptions were configured as test errors.

### Clean verification result

Command:

uv run pytest tests/integration/test_taskguard_local_eval.py -v -s

Result:

6 passed, 11 warnings in 128.82s

The clean run contained no:

- 429 Too Many Requests
- ResourceExhausted error
- PytestUnhandledThreadExceptionWarning

The remaining warnings came from Google ADK and Google GenAI dependency features and deprecations.

### Git checkpoint

bbbefba Add TaskGuard local evaluation suite

---

## 2026-06-24 — Specification recovery and quota-safe evaluation

### As-built specification

Created the authoritative TaskGuard specification:

`SPEC.md`

The specification records:

* the TaskGuard business purpose and intended users
* the evidence-based agent workflow
* the deterministic validation-tool contract
* security boundaries and explicit non-goals
* automated evaluation scenarios
* the three official submission demonstrations
* the bounded Antigravity audit role
* submission acceptance criteria
* the anti-drift change-control rule

Git checkpoint:

`d92f463 Add TaskGuard as-built specification`

### Quota-safe evaluation-dataset test

The evaluation-dataset structure test previously lived inside the live Gemini
evaluation module. Because that module skipped at import time when no Gemini
API key was available, the deterministic dataset test was also skipped.

Moved the dataset-structure assertion into:

`tests/unit/test_eval_dataset.py`

The five live TaskGuard evaluation cases remain in:

`tests/integration/test_taskguard_local_eval.py`

They continue to require:

* `GEMINI_API_KEY` or `GOOGLE_API_KEY`
* `RUN_LIVE_GEMINI_TESTS=TRUE`

### No-key verification

Command:

`env -u GEMINI_API_KEY -u GOOGLE_API_KEY uv run pytest -v`

Verified result:

`8 passed, 3 skipped, 4 warnings in 1.16s`

This confirms that:

* deterministic validation tests run without Gemini credentials
* the evaluation-dataset structure test runs without Gemini credentials
* no live Gemini request is made by the default no-key suite
* live integration and evaluation modules remain skipped

Git checkpoint:

`17a6269 Make evaluation dataset test quota safe`
