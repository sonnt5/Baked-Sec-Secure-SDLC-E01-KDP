# Lab 2: Supply Chain Risk Management (SCA) & Automated Remediation
**Book:** Bake Security into Modern Software Development
**Chapter 9:** Secure Continuous Integration/Continuous Delivery

## Introduction

Modern applications rely heavily on third-party libraries — a typical Node.js project can pull in hundreds of transitive dependencies. The 2021 Log4Shell vulnerability (CVE-2021-44228) demonstrated how a single vulnerable dependency buried deep in the supply chain can expose millions of systems. Without Software Composition Analysis (SCA), teams remain blind to known vulnerabilities hiding in their dependency tree.

This lab addresses supply chain security as described in Chapter 9's coverage of Security Gates Integration and SCA. You will learn to detect vulnerable dependencies using automated tools and set up Dependabot for continuous remediation. This directly supports the **Integrity** pillar of the CIA Triad — ensuring that the components you ship are free from known exploitable flaws.

The Shift-Left approach applies here too: rather than discovering a vulnerable `lodash` version in a production incident, your CI pipeline will catch it at the Pull Request stage and block the merge until the issue is resolved.

## 1. Objective
Practice Software Composition Analysis (SCA) to detect vulnerabilities in third-party libraries and understand the process of automated dependency updates (Automated Remediation) to reduce the workload on development teams.

**Key skills:**
*   Using SCA tools (Trivy/npm audit).
*   Configuring Dependabot for automated remediation.
*   Understanding Dependency Locking.

## 2. Prerequisites
*   Continue using the repository from Lab 1 or create a new one.
*   Understanding of `package.json` and `package-lock.json`.

## 3. Scenario
Your project is using an old version of the `lodash` library (v4.17.15) that has multiple known **Critical** and **High** severity CVEs, including Prototype Pollution (CVE-2020-8203) and Command Injection vulnerabilities. Without SCA, the team has no visibility into these risks — the application builds and tests pass normally, giving a false sense of security.

You need to: (1) integrate SCA scanning into the CI pipeline so vulnerable dependencies automatically **fail** the build, and (2) configure Dependabot to propose version bumps as Pull Requests, creating an automated **Detection -> Patch -> Verify -> Remediate** workflow.

## 4. Step-by-step Instructions

### Step 1: Install a Vulnerable Library (Simulation)
1.  Open `package.json`, edit or add a dependency:
```json
"dependencies": {
  "lodash": "4.17.15"
}
```
*(Version 4.17.15 has multiple known CVEs)*.
2.  Run `npm install`.

> **Expected Output:** After running `npm install`, you can immediately check with `npm audit`:
> ```
> $ npm audit
>
> lodash  <=4.17.20
> Severity: critical
> Prototype Pollution in lodash - https://github.com/advisories/GHSA-jf85-cpcp-j695
> Command Injection in lodash - https://github.com/advisories/GHSA-35jh-r3h4-6jhm
> Regular Expression Denial of Service in lodash - https://github.com/advisories/GHSA-x5rq-j2xg-h7qm
> fix available via `npm audit fix`
>
> 3 vulnerabilities (1 moderate, 1 high, 1 critical)
> ```

### Step 2: Run SCA Manually and in the Pipeline
1.  On your local machine, run: `npm audit`. You will see a report of High/Critical vulnerabilities.
2.  Integrate `Trivy` into GitHub Actions. Add a job to `.github/workflows/ci.yml`:

```yaml
  sca-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Trivy vulnerability scanner in repo mode
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          ignore-unfixed: true
          format: 'table'
          exit-code: '1' # Fail pipeline if vulnerabilities are found
          severity: 'CRITICAL,HIGH'
```
3.  Commit and push.
4.  **Expected result:** The pipeline will **FAIL** because vulnerabilities were detected in `lodash`.

> **Expected Output:** The Trivy step in CI will produce output similar to:
> ```
> 2024-01-15T10:30:00.000Z  INFO  Vulnerability scanning is enabled
> 2024-01-15T10:30:02.000Z  INFO  Detected OS: debian
> 2024-01-15T10:30:02.000Z  INFO  Number of language-specific files: 1
> 2024-01-15T10:30:02.000Z  INFO  Detecting npm vulnerabilities...
>
> package-lock.json (npm)
> =======================
> Total: 3 (HIGH: 1, CRITICAL: 2)
>
> ┌─────────┬────────────────┬──────────┬────────┬───────────────────┬─────────────────┬──────────────────────────────────────┐
> │ Library │ Vulnerability  │ Severity │ Status │ Installed Version │ Fixed Version   │ Title                                │
> ├─────────┼────────────────┼──────────┼────────┼───────────────────┼─────────────────┼──────────────────────────────────────┤
> │ lodash  │ CVE-2020-8203  │ HIGH     │ fixed  │ 4.17.15           │ 4.17.20         │ Prototype Pollution                  │
> │ lodash  │ CVE-2021-23337 │ CRITICAL │ fixed  │ 4.17.15           │ 4.17.21         │ Command Injection                    │
> │ lodash  │ CVE-2020-28500 │ CRITICAL │ fixed  │ 4.17.15           │ 4.17.21         │ Regular Expression DoS               │
> └─────────┴────────────────┴──────────┴────────┴───────────────────┴─────────────────┴──────────────────────────────────────┘
>
> Error: Process completed with exit code 1.
> ```

### Step 3: Configure Dependabot (Automated Remediation)
Instead of fixing manually, let the bot handle it.
1.  Create the file `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
```
2.  Commit and push this file to the main branch.
3.  Go to **Settings > Code security and analysis** on GitHub, and enable **Dependabot alerts** and **Dependabot security updates** (if not already enabled).

### Step 4: Observe and Process
1.  Wait a few minutes (or trigger manually), and Dependabot will scan the repo.
2.  Go to the **Pull Requests** tab — you will see a new PR created by the bot: *Bump lodash from 4.17.15 to 4.17.21...*

> **Expected Output:** The Dependabot PR will contain details like:
> ```
> Bump lodash from 4.17.15 to 4.17.21
>
> Bumps lodash from 4.17.15 to 4.17.21.
>
> Release notes:
>   Sourced from lodash's releases.
>   - 4.17.21: Fixed command injection (CVE-2021-23337)
>   - 4.17.20: Fixed prototype pollution (CVE-2020-8203)
>
> Changelog:
>   Sourced from lodash's changelog.
>
> Commits:
>   See full diff in compare view
>
> Dependabot will resolve any conflicts with this PR as long as
> you don't alter it yourself.
> ```

3.  Click on the PR, review the **Files changed** and **Check status** (the CI pipeline will run on this PR to ensure the patch does not break the app).
4.  If CI is green, perform **Merge Pull Request**.

## 5. What You Learned

*   **Software Composition Analysis (SCA)** provides visibility into known vulnerabilities in third-party dependencies — risks that are invisible to unit tests and functional testing.
*   Tools like `npm audit` and **Trivy** can be integrated as CI Security Gates, automatically blocking merges when Critical/High severity CVEs are detected in the dependency tree.
*   **Dependabot** automates the remediation workflow by creating Pull Requests with version bumps, reducing manual effort and ensuring patches are applied promptly.
*   **Dependency Locking** (`package-lock.json`) is critical for reproducible builds — it ensures every CI run and every developer uses the exact same dependency versions.
*   The full SCA workflow — **Detection -> Patch Proposal -> CI Verification -> Merge** — creates a closed-loop system for managing supply chain risk continuously.

## 6. Answer Key / Solution Repository
- **Repository:** https://github.com/maycuatroi1/sca-remediation-lab
- **`main` branch:** Complete working solution (all security gates pass)
- **`vulnerable` branch:** Intentionally vulnerable code for testing gates
