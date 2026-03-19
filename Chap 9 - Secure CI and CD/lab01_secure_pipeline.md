# Lab 1: Building a Basic Secure Pipeline with Security Gates
**Book:** Bake Security into Modern Software Development
**Chapter 9:** Secure Continuous Integration/Continuous Delivery

## Introduction

In modern software development, a CI/CD pipeline that only builds and tests for functionality is no longer sufficient. The 2021 Codecov breach demonstrated how attackers can exploit an unprotected pipeline to exfiltrate secrets from thousands of repositories. Without security gates, vulnerable code, leaked API keys, and insecure dependencies slip silently into production.

This lab puts the **Shift-Left** principle into practice: instead of discovering security issues after deployment, you will embed automated checks directly into the pipeline. By treating the pipeline as code (Chapter 9, Section 4), every push triggers secret detection, static analysis, and linting — forming the first line of defense described in the OWASP CI/CD Top 10 (CICD-SEC-4: Poisoned Pipeline Execution).

The CIA Triad applies here directly: **Confidentiality** is protected by blocking leaked secrets, **Integrity** is enforced by rejecting code with known vulnerabilities, and **Availability** is maintained by catching issues before they reach production.

## 1. Objective
In this lab, you will learn how to build a basic CI/CD pipeline following the "Pipeline as Code" model and integrate Security Gates to detect security issues early when code is pushed (Shift-Left).

**Key skills:**
*   Setting up a GitHub Actions Workflow.
*   Integrating Secret Detection (detecting exposed secrets).
*   Integrating SAST (Static Application Security Testing).
*   Integrating Linting to ensure code quality.

## 2. Prerequisites
*   A GitHub account.
*   Basic knowledge of Git and the command line.
*   An IDE (VS Code is recommended).

### Getting Started
Download the starter project and set up your own repository:
1.  Download the starter code from: https://github.com/sonnt5/Baked-Sec-Secure-SDLC-E01-KDP/tree/main/Labworks/Chap%209%20-%20Secure%20CI%20and%20CD/secure-ci-lab
2.  Create a **new repository** on your GitHub account (e.g., `secure-ci-lab`).
3.  Initialize git and push the starter code:
```bash
cd secure-ci-lab
git init
git remote add origin https://github.com/<YOUR_USERNAME>/secure-ci-lab.git
git add .
git commit -m "Initial commit: starter code for Lab 1"
git branch -M main
git push -u origin main
```
*   Node.js installed (to run code locally if needed).

## 3. Scenario
You are a DevOps Engineer responsible for setting up a pipeline for a simple web backend project using Node.js/Express. Currently, the project has **no security checks** — any team member can accidentally commit hardcoded API keys, use dangerous functions like `eval()`, or push code with injection vulnerabilities, and the pipeline will happily pass with a green checkmark.

Your task is to add three Security Gates to the pipeline: (1) **Secret Detection** to prevent credential leaks, (2) **SAST scanning** to catch dangerous code patterns, and (3) **Linting** to enforce code quality. After completing this lab, any commit containing secrets or insecure code will automatically fail the pipeline, preventing it from reaching the main branch.

## 4. Step-by-step Instructions

### Step 1: Initialize the Repository and Sample Code
1.  Create a new repository on GitHub (e.g., `secure-ci-lab`).
2.  Clone it to your machine and create a simple `app.js` file:

```javascript
// app.js
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  const name = req.query.name || 'World';
  // Potential vulnerability: XSS or Code Injection if eval is used (simulated)
  // console.log("User input: " + name);
  res.send(`Hello ${name}!`);
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
```

3.  Create a `package.json` file:
```json
{
  "name": "secure-ci-lab",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 0"
  },
  "dependencies": {
    "express": "^4.17.1"
  }
}
```

### Step 2: Set Up a Basic GitHub Actions Workflow
Create the file `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Use Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16.x'
    - run: npm ci
    - run: npm test
```
Commit and push to GitHub. Check the **Actions** tab to ensure the pipeline runs green (succeeds).

> **Expected Output:** In the Actions tab, you should see a successful workflow run:
> ```
> CI Pipeline ✓
>   build ✓
>     ✓ Set up job (2s)
>     ✓ Run actions/checkout@v3 (1s)
>     ✓ Use Node.js (3s)
>     ✓ Run npm ci (5s)
>     ✓ Run npm test (1s)
> ```

### Step 3: Integrate the Secret Detection Gate
We will use `gitleaks` or `trufflehog` to scan for secrets. Here we use the `gitleaks` action.

Update `.github/workflows/ci.yml`, adding a `security` job:

```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Important for scanning commit history
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Challenge:**
1.  Create a file `config.js` and add the line: `const apiKey = "AKIAIOSFODNN7EXAMPLE";` (this follows the format of a fake AWS Key).
2.  Commit and push.
3.  **Expected result:** The pipeline on GitHub Actions will **FAIL** at the Gitleaks step. You have successfully blocked a secret from leaking!

> **Expected Output:** The Gitleaks step will fail with output similar to:
> ```
> Finding:     const apiKey = "AKIAIOSFODNN7EXAMPLE"
> Secret:      AKIAIOSFODNN7EXAMPLE
> RuleID:      aws-access-key-id
> Entropy:     3.52
> File:        config.js
> Line:        1
> Fingerprint: config.js:aws-access-key-id:1
>
> 1 leaks found in 1 commits.
> Error: Process completed with exit code 1.
> ```

4.  **Remediation:** Delete the file or the line containing the key, then commit again to make the pipeline green.

### Step 4: Integrate the SAST Gate (Semgrep)
Add the Semgrep tool to scan for code vulnerabilities. Add a step to the `security` job or create a new job:

```yaml
  sast-scan:
    runs-on: ubuntu-latest
    container:
      image: returntocorp/semgrep
    steps:
      - uses: actions/checkout@v3
      - run: semgrep scan --config=auto .
```

**Challenge:**
1.  Edit `app.js`, adding a dangerous line: `eval(req.query.code);`
2.  Commit and push.
3.  **Expected result:** Semgrep will detect the use of `eval()` (an RCE risk) and may fail the pipeline or flag a warning in the logs.

> **Expected Output:** Semgrep will report findings similar to:
> ```
>   app.js
>     javascript.lang.security.detect-eval-with-expression
>       Detected eval() with a non-literal argument. If this data can be
>       controlled by an external source, this is a code injection
>       vulnerability. Avoid eval() if possible or ensure the evaluated
>       expression is not user-controllable.
>       Details: https://sg.run/xxxx
>
>        7│   eval(req.query.code);
>
> Findings: 1 error, 0 warnings
> Error: Process completed with exit code 1.
> ```

## 5. What You Learned

*   **Pipeline as Code** allows you to version-control your CI/CD configuration alongside your application code, making security gates reproducible and auditable.
*   **Secret Detection** (Gitleaks) acts as an automated guardrail that prevents credential leaks before they reach the repository history — a key Confidentiality control.
*   **SAST scanning** (Semgrep) catches dangerous code patterns like `eval()` at the source level, embodying the Shift-Left principle by finding vulnerabilities before runtime.
*   **Security Gates** transform a basic build pipeline into a Secure CI/CD pipeline by creating automated checkpoints that enforce security standards on every commit.
*   Combining multiple gates (secrets + SAST + linting) provides **Defense in Depth** — if one gate misses an issue, another can catch it.

## 6. Answer Key / Solution Repository
- **Solution branch:** [`chap9-solution`](https://github.com/sonnt5/Baked-Sec-Secure-SDLC-E01-KDP/tree/chap9-solution/Labworks/Chap%209%20-%20Secure%20CI%20and%20CD/secure-ci-lab) — complete working solution with all security gates passing
- **`secure-ci-lab/`:** Contains `app.js`, `.github/workflows/ci.yml`, `.eslintrc.json`, `package.json`, etc.
- **`secure-ci-lab/vulnerable-branch/`:** Intentionally vulnerable code for testing gates — `config.js` (fake AWS key) and modified `app.js` (with `eval()`)
