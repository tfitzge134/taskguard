
# TaskGuard Specification

## Document status

This is the authoritative as-built specification for TaskGuard.

It consolidates the verified implementation, project decisions, safety
boundaries, testing strategy, submission scope, and remaining acceptance
criteria.

* Project: TaskGuard
* Track: Agents for Business
* Target submission date: July 1, 2026
* Official deadline: July 6, 2026
* Implementation status: Core MVP implemented and tested
* Current project phase: Specification recovery and submission packaging

## 1. Problem statement

Software teams frequently receive SQL schema files that contain policy,
quality, or safety problems. Manually identifying those problems can be slow
and inconsistent.

TaskGuard is a Google ADK agent that safely validates a requested SQL schema
file and explains the result using evidence returned by a deterministic
validation tool.

TaskGuard must never guess whether a schema is valid. It must run the approved
validation tool and ground its response in the returned status, exit code, and
evidence.

## 2. Business value

TaskGuard demonstrates how an evidence-based agent can help software and data
teams:

* identify schema-policy violations
* produce repeatable validation evidence
* reduce unsupported debugging claims
* reject unsafe file requests
* recommend one focused remediation step
* preserve human control over file changes

The MVP focuses on safe diagnosis rather than autonomous repair.

## 3. Intended users

Primary users include:

* software developers
* database developers
* data engineers
* code reviewers
* technical team leads

## 4. Core project scope

TaskGuard validates one relative SQL file located inside the approved project
directory.

The MVP includes:

* one Google ADK agent
* one deterministic schema-validation tool
* one local SQL policy validator
* structured tool results
* evidence-based agent explanations
* deterministic unit tests
* live Google ADK integration tests
* five automated evaluation scenarios
* three official submission demonstrations
* a bounded Antigravity audit skill

## 5. Development workflow

All project changes must follow:

1. Audit
2. Investigate
3. Test
4. Implement
5. Re-test
6. Inspect the diff
7. Commit the verified checkpoint

An inference is not proof.

Files, logs, test output, and Git state must be inspected before implementing
a fix.

Only confirmed issues may result in code changes.

## 6. Agent workflow

For every schema-validation request, TaskGuard must follow:

1. AUDIT: Identify the exact requested schema file.
2. INVESTIGATE: Do not assume that the schema passes or fails.
3. TEST: Call `run_schema_validation`.
4. EXPLAIN: Use only the returned status, exit code, and evidence.
5. RECOMMEND: Provide one focused next debugging action when remediation is
   needed.

## 7. Architecture

The core architecture is:

User request
→ Google ADK TaskGuard agent
→ `run_schema_validation`
→ `validate_schema.py`
→ structured result
→ evidence-based TaskGuard response

Core files:

* `app/agent.py`
* `app/tools.py`
* `validate_schema.py`
* `good_schema.sql`
* `bad_schema.sql`

Supporting files:

* `README.md`
* `PROJECT_LOG.md`
* `.agents/skills/taskguard-audit/SKILL.md`
* `tests/unit/test_tools.py`
* `tests/integration/test_agent.py`
* `tests/integration/test_taskguard_local_eval.py`
* `tests/eval/datasets/basic-dataset.json`
* `tests/eval/eval_config.yaml`

## 8. Agent configuration

The local MVP uses:

* Google ADK
* Google AI Studio authentication
* Gemini model `gemini-2.5-flash`
* `GEMINI_API_KEY` or `GOOGLE_API_KEY`
* `GOOGLE_GENAI_USE_VERTEXAI=FALSE`

A billing-enabled Google Cloud project is not required for the local MVP.

## 9. Validation-tool input contract

The tool accepts:

* one string containing a relative path
* a path ending in `.sql`
* a file located within the approved project directory
* an existing regular file

Example accepted input:

`good_schema.sql`

## 10. Validation-tool rejection rules

The tool must reject:

* absolute paths
* directory traversal containing `..`
* non-SQL file extensions
* paths outside the approved project directory
* missing SQL files

A rejected request must not execute the validator.

## 11. Validation execution contract

For an accepted SQL file, the tool must:

* use a fixed subprocess argument list
* use the current Python interpreter
* invoke only `validate_schema.py`
* avoid shell execution
* use the project directory as the working directory
* enforce a ten-second timeout
* capture standard output
* capture standard error
* capture the exit code
* avoid modifying the requested file

## 12. Structured result contract

The tool returns a dictionary containing:

* `status`
* `schema_file`
* `command_run`
* `exit_code`
* `stdout`
* `stderr`
* `evidence`
* `file_modified`

Supported statuses are:

* `passed`
* `failed`
* `rejected`
* `error`

Status meanings:

* `passed`: validation ran and returned exit code 0
* `failed`: validation ran and returned a nonzero exit code
* `rejected`: the request violated a safety or input rule, and no validation
  command ran
* `error`: validation could not complete, including timeout conditions

## 13. SQL validation policy

The current validator enforces three policies:

1. `DROP TABLE` statements are forbidden.
2. Table names must use snake_case.
3. Every table must contain a primary key named `id`.

Successful validation prints:

`Schema validation passed.`

A successful validation returns exit code 0.

A policy failure prints every detected violation and returns exit code 1.

## 14. Agent response contract

TaskGuard must:

* call the validation tool before declaring success or failure
* accurately distinguish passed, failed, rejected, and error results
* report the exit code when one is available
* report returned evidence accurately
* state that no validation command ran for rejected requests
* avoid claiming that files were modified
* avoid inventing evidence
* avoid bypassing restrictions
* provide one focused next action when remediation is needed
* keep responses concise and practical

For a failed schema, the preferred response sections are:

* Status
* Evidence
* Explanation
* Recommended next step

## 15. Safety boundaries

TaskGuard must not:

* execute arbitrary shell commands
* accept unrestricted filesystem paths
* read files outside the approved project directory
* validate non-SQL files
* modify schema files
* autonomously repair code or schemas
* expose API keys or credentials
* print environment secrets
* claim that an action occurred without tool evidence
* bypass validation restrictions

## 16. Verified schema examples

### Valid schema

`good_schema.sql`:

* status: passed
* exit code: 0
* evidence: schema validation passed

### Invalid schema

`bad_schema.sql` returns:

* `DROP TABLE` statements are forbidden
* table `userProfile` must be snake_case
* table `posts` is missing a primary key named `id`
* exit code: 1

## 17. Automated evaluation scenarios

The automated evaluation dataset contains five cases:

1. Valid schema passes.
2. Invalid schema reports every returned violation.
3. Directory traversal is rejected.
4. A non-SQL file is rejected.
5. A missing SQL file is rejected.

All five remain part of automated coverage.

## 18. Official submission demonstrations

The public Writeup and demonstration video will focus on three cases:

1. Valid schema passes.
2. Invalid schema reports complete evidence.
3. Unsafe directory traversal is rejected.

The non-SQL and missing-file cases remain automated tests but are not required
as primary video demonstrations.

## 19. Testing strategy

### Deterministic tests

Deterministic tool tests must not use Gemini quota.

They verify:

* valid-schema success
* invalid-schema evidence
* directory-traversal rejection
* absolute-path rejection
* non-SQL-file rejection
* missing-file rejection

### Live Gemini tests

Tests that invoke Gemini must be opt-in.

They require:

* `GEMINI_API_KEY` or `GOOGLE_API_KEY`
* `RUN_LIVE_GEMINI_TESTS=TRUE`

Live cases are paced to reduce per-minute free-tier failures.

Daily free-tier limits may still prevent a live run.

### No-key collection behavior

When neither Gemini key is present, the current integration and local-evaluation
modules skip at module level.

The verified no-key collection result is:

* seven deterministic tests collected
* no Gemini request made

Because the local-evaluation module skips at module level, its dataset-structure
test is not currently collected without a Gemini key.

This is a confirmed conformance item to evaluate after this specification is
created.

### Optional Vertex runtime

Vertex AI Agent Engine tests are optional.

They require:

* `RUN_VERTEX_RUNTIME_TESTS=TRUE`
* a configured Google Cloud project
* billing
* required Vertex AI permissions

They are not part of the local MVP acceptance criteria.

## 20. Verified test results

Latest verified quota-safe suite with an API key available and live tests not
enabled:

`8 passed, 7 skipped, 4 warnings in 1.37s`

Latest verified live local evaluation:

`6 passed, 11 warnings in 128.82s`

Latest verified no-key collection:

`7 tests collected in 1.00s`

Warnings from experimental or deprecated Google ADK and Google GenAI
dependency features do not represent TaskGuard validation failures.

## 21. Antigravity audit role

Antigravity is a bounded repository auditor.

It must use:

`.agents/skills/taskguard-audit/SKILL.md`

Antigravity may:

* inspect approved project files
* review tests and security controls
* compare implementation with this specification
* report confirmed findings
* report clearly labeled unverified concerns
* recommend one focused next action

Antigravity must not:

* edit files
* execute arbitrary shell commands
* expose credentials
* redesign the project
* add features
* control implementation direction
* treat an inference as proof

Every Antigravity finding must be independently inspected, reproduced, and
tested before implementation.

## 22. Known limitations

The MVP has the following limitations:

* It validates SQL using regular expressions rather than a complete SQL parser.
* It supports only the three current schema policies.
* It validates only files inside the local project directory.
* It does not repair schemas automatically.
* It does not provide long-term memory.
* It does not use RAG or a vector database.
* Live Gemini tests depend on external API quota.
* Cloud deployment is not required for the MVP.
* The repository contains optional Vertex and Terraform starter scaffolding
  that is separate from the local TaskGuard core.
* `tests/unit/test_dummy.py` is a starter placeholder and is not meaningful
  TaskGuard coverage.

## 23. Conformance review status

The Stage 2 conformance review produced these results:

1. The missing `frontend` directory is optional, non-blocking configuration
   cleanup. The project builds successfully, and the generated wheel contains
   only the real `app` package.
2. The evaluation-dataset structure test was moved to
   `tests/unit/test_eval_dataset.py`, so it now runs without Gemini credentials.
3. README documents the verified no-key result and the explicit live-test
   command.
4. PROJECT_LOG records `SPEC.md`, commit `17a6269`, and the quota-safe
   evaluation-dataset test.

The current verified no-key result is:

`8 passed, 3 skipped, 4 warnings in 1.16s`

Optional configuration cleanup must not delay submission.

## 24. Explicit non-goals

The MVP will not include:

* a large multi-agent system
* RAG
* a vector database
* long-term agent memory
* unrestricted autonomous code editing
* a Cloud Run frontend
* Pub/Sub
* Kubernetes
* mandatory cloud deployment
* a rebuilt Homework 4 expense agent
* optional codelabs completed only for their own sake

No non-goal should be added before the required submission package is complete.

## 25. Submission package

The final submission package will contain:

* public GitHub repository
* working source code
* `README.md`
* `SPEC.md`
* dependency files
* `uv.lock`
* automated tests
* three demonstration cases
* example debugging reports
* architecture diagram
* Kaggle Writeup within 2,500 words
* YouTube demonstration no longer than five minutes
* cover image

## 26. Acceptance criteria

TaskGuard is ready for submission when:

* the core validation tool passes deterministic tests
* the agent uses tool evidence rather than assumptions
* unsafe requests are rejected
* no file is modified
* README commands match actual behavior
* PROJECT_LOG reflects the final verified status
* code and tests conform to this specification
* three demonstration reports are prepared
* the final bounded Antigravity audit is complete
* every accepted Antigravity finding has been independently verified
* the repository contains no exposed secrets
* the architecture diagram is final
* the Writeup is complete
* the cover image is complete
* the demonstration video is no longer than five minutes
* the public repository is accessible
* the submission is completed by the target date

## 27. Change-control rule

This specification now controls the remaining TaskGuard work.

Any proposed new feature must be classified as:

* required for conformance
* required for submission
* optional improvement
* out of scope

Optional and out-of-scope work must not delay the submission.
