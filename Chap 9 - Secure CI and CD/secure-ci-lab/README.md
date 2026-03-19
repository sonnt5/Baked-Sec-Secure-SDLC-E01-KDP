# Lab 1: Secure Pipeline with Security Gates (Answer Key)

## Overview
This repository is the **answer key** for Lab 1 of Chapter 9 (Secure CI/CD).

Students build a basic CI/CD pipeline with **Security Gates**: Secret Detection (Gitleaks), SAST (Semgrep), and Linting.

## Branches

### `main` — Complete Working Solution
- Clean Express app with no vulnerabilities
- CI pipeline with build, security (Gitleaks), and SAST (Semgrep) jobs
- **Expected result: All pipeline jobs pass (green)**

### `vulnerable` — Intentionally Vulnerable Code
Contains deliberately introduced vulnerabilities for testing security gates:
- `config.js`: Contains a fake AWS key `AKIAIOSFODNN7EXAMPLE` → **triggers Gitleaks**
- `app.js`: Contains `eval(req.query.code)` → **triggers Semgrep SAST**
- **Expected result: Pipeline FAILS at security and sast-scan jobs**

## Pipeline Jobs (`ci.yml`)
1. **build** — Checkout, setup Node.js 18, `npm ci`, `npm test`
2. **security** — Gitleaks secret detection (full history scan)
3. **sast-scan** — Semgrep static analysis (auto config)

## How to Use
1. Fork this repository
2. Switch to `vulnerable` branch to see security gates catch issues
3. Switch back to `main` to see a clean, passing pipeline
