# Lab 7.3 — Injection Prevention: SQL, Command, Template, ReDoS

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Submission pipeline code | Output: Injection-Free Code + ASVS V1.2 Checklist

> [!NOTE]
> **OWASP ASVS v5.0.0:** V1.2.4 — parameterized queries or ORM. V1.2.5 — parameterized OS queries (`shell=False`). V1.2.9 — regex special characters escaped; ReDoS protection.

## Learning Objectives

- Identify all injection sinks in the CODING WAR submission pipeline.
- Understand the Source → Validation → Encoding/Parameterization → Sink model.
- Fix SQL injection using SQLAlchemy ORM.
- Fix Command injection using the subprocess list API.
- Fix ReDoS using regex analysis and timeout.
- Complete the ASVS V1.2 checklist for CODING WAR.

---

## Task 1 — Injection Sink Inventory

| ID | Sink Type | Location (file + function) | Untrusted Source | Vulnerable Pattern | ASVS Control + Fix |
|----|----------|---------------------------|-----------------|-------------------|--------------------|
| **IS-01** | SQL Query (DB Engine) | `app/repositories/submission_repo.py` `get_submissions_by_contest()` | `sort` field from `GET /submissions?sort=score_asc` — user-controlled | `f"ORDER BY {sort_field} DESC"` — ORDER BY cannot be directly parameterized | V1.2.4 — Allowlist for sort fields: only `{'score','time','penalty'}` allowed; not parameterized |
| **IS-02** | SQL Query | `app/repositories/problem_repo.py` `search_problems()` | `q` from `GET /problems?q=...` — public endpoint | `db.execute(f'SELECT * FROM problems WHERE title LIKE "%{q}%"')` | V1.2.4 — Use SQLAlchemy: `db.query(Problem).filter(Problem.title.ilike(f'%{q}%'))` |
| **IS-03** | OS Command (Shell) | `app/services/judge_service.py` `compile_code()` | language choice + source file path from submission | `subprocess.run(f'python {file_path} --timeout {timeout}', shell=True)` | V1.2.5 — subprocess list API: `subprocess.run(['python', str(file_path), '--timeout', str(timeout)], shell=False)` |
| **IS-04** | Template Engine (Jinja2) | `app/templates/result_email.html` `render_result_email()` | `problem_title` from contest config — admin-controlled but not sanitized | `Template(f'Congratulations on solving {problem_title}!').render()` | V1.3.7 — Use Environment with `autoescape=True`; NEVER `Template(user_string).render()`; use `env.get_template()` |
| **IS-05** | Regex Engine (ReDoS) | `app/validators/code_validator.py` `check_output_format()` | Contestant output (contestant-controlled) matched against problem-defined regex | `re.match(pattern, contestant_output)` — pattern from problem DB, output from contestant | V1.2.9 — Use `re.compile()` with timeout via `threading`; validate patterns against ReDoS: check for nested quantifiers |
| **IS-06** | \[Team identifies additional sink\] | | | | |

---

## Task 2 — SQL Injection Fix (IS-01 and IS-02)

IS-01 is an interesting case: `ORDER BY` cannot be parameterized. This is a case ASVS v5 notes specially: *"Query parts such as table and column names cannot be escaped — using escaped user-supplied data results in failed queries or SQL injection."*

Study [`code/fixed/submission_repo.py`](../code/fixed/submission_repo.py) and answer:
1. Explain in your own words why ORDER BY cannot be parameterized, and why the allowlist approach is the correct fix.
2. In `search_problems()`, what is the difference between `f"%{q}%"` being inside `ilike()` vs being inside an f-string in `db.execute(f"... WHERE title LIKE '{q}'")`?
3. Add IS-06 — identify one more SQL injection sink in the CODING WAR codebase that the team can find through manual review.

---

## Task 3 — Command Injection Fix (IS-03)

Study [`code/fixed/judge_service.py`](../code/fixed/judge_service.py).

The fix has 5 key elements — identify each and explain why it is necessary:

| Element | Code location | Why necessary |
|---------|--------------|---------------|
| `shell=False` | `subprocess.run(..., shell=False)` | |
| Absolute interpreter path | `ALLOWED_LANGUAGES` dict | |
| `env={}` | `subprocess.run(..., env={})` | |
| `cwd="/sandbox"` | `subprocess.run(..., cwd="/sandbox")` | |
| Language allowlist check | `if interpreter is None: raise ValueError` | |

---

## Task 4 — ReDoS Analysis & Fix (IS-05)

Study [`code/fixed/code_validator.py`](../code/fixed/code_validator.py).

1. Why does the vulnerable pattern `r"([a-zA-Z]+)*"` cause catastrophic backtracking? Trace through what happens with input `"aaaaaaaaX"`.
2. The `safe_regex_match()` function uses a threading timeout. What is the limitation of this approach compared to a pre-compiled linear pattern?
3. Why does `EXPECTED_VERDICT_PATTERN = re.compile(r"^(ACCEPTED|WRONG_ANSWER|TLE|MLE|RE)$")` avoid ReDoS? What properties make it linear-time?

---

## Task 5 — ASVS V1.2 Injection Prevention Compliance Checklist

| ASVS ID | Control | Status | Evidence / Gap |
|---------|---------|--------|---------------|
| **1.2.1** | Output encoding for HTTP response is context-appropriate | Partial | Jinja2 with autoescape: PLANNED (IS-04). Direct response strings: no auto-encoding. Gap: enforce Jinja2 autoescape for all templates. |
| **1.2.2** | Untrusted data in URLs is encoded appropriately | Yes | FastAPI URL encoding for path/query parameters. Opaque IDs prevent enumeration. Evidence: ADR-001. |
| **1.2.4** | SQL queries use parameterized queries/ORM — protected from SQLi | Partial | IS-02: SQLAlchemy ilike — fixed. IS-01: ORDER BY uses column allowlist — fixed. Gap: audit remaining raw SQL in legacy migration scripts. |
| **1.2.5** | Application protected against OS command injection | Fail → Fixed | IS-03: `shell=True` subprocess — fixed in Lab 7.3 Task 3. Evidence: `judge_service.py` fix. Remaining gap: verify no `shell=True` elsewhere (SAST scan required). |
| **1.2.7** | Protected against XPath injection | N/A | No XPath usage in CODING WAR. N/A justified. |
| **1.2.9** | Special characters in regex escaped; ReDoS protection | Fail → Partial | IS-05: output format validation with user-pattern risks. Fixed with timeout. Gap: audit all `re.match`/`re.search` calls for nested quantifiers (SAST rule needed). |
| **1.2.10** | Protected against CSV and Formula Injection | Partial | Contest results export to CSV: NOT YET IMPLEMENTED. When implemented: must escape fields starting with `= + - @`. Gap: implement at export endpoint. |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Injection Sink Inventory (5+ sinks) | **20** | Each sink: source→sink chain clear (2 pts), vulnerable pattern identified specifically (2 pts), ASVS control cited (1 pt) |
| SQL Injection Fix analysis (IS-01 + IS-02) | **25** | IS-01: explains WHY ORDER BY cannot be parameterized (10 pts). IS-02: SQLAlchemy ilike explanation is correct (15 pts) |
| Command Injection Fix analysis (IS-03) | **20** | All 5 elements explained: shell=False, absolute paths, empty env, cwd, allowlist check (4 pts each) |
| ReDoS Analysis + Fix | **20** | Vulnerable pattern backtracking explained (8 pts); timeout approach implements Fail Securely (6 pts); linear alternative explained (6 pts) |
| ASVS V1.2 Checklist | **15** | Honest assessment: N/A items have justification; Fail items have specific gap; not all "Yes" without evidence |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.3.md](../solutions/sol-7.3.md)*
