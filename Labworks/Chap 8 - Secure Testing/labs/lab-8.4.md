# Lab 8.4 — Supply Chain Security: SCA + Container + Secrets

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: `requirements.txt` + `Dockerfile` + CODING WAR source tree
> Output: SCA Report + SBOM + Secrets Scan Report + Dependency Response Playbook

## Learning Objectives

- Run pip-audit, Trivy, and detect-secrets and interpret their output in context.
- Distinguish "patch immediately" from "monitor" from "accept with documentation."
- Understand what an SBOM is and what questions it can answer.
- Build a response playbook that the team can actually use under pressure.

## Code Files

| File | Role |
|------|------|
| `code/config/trivy-config.yaml` | Trivy scan configuration |

---

## Task 1 — SCA with pip-audit

```bash
pip install pip-audit --break-system-packages
pip-audit --requirement requirements.txt --format json -o sca-results.json
pip-audit --requirement requirements.txt --format cyclonedx-json -o sbom.json
```

For each finding: look up the CVE. Assess whether it is exploitable in CODING WAR's specific usage of the library — not just whether the CVE exists. A vulnerability in a function that CODING WAR never calls is not the same risk as one in a function called on every request.

Cross-reference your findings with the dependency audit from Lab 7.5. Where Lab 7.5 identified issues, does pip-audit confirm them? Where it does not, explain the gap.

---

## Task 2 — Container Image Scan with Trivy

```bash
trivy image --config code/config/trivy-config.yaml coding-war:latest
trivy fs --config code/config/trivy-config.yaml .
```

Review `code/config/trivy-config.yaml` before running — understand what is being suppressed and why.

For the findings Trivy produces, triage each one against CODING WAR's actual deployment. An OS package CVE in a library that is not loaded by the Python runtime is a different risk than a CVE in a library that processes untrusted input. Document your reasoning.

Pay particular attention to Dockerfile misconfigurations — these are often more immediately fixable than OS CVEs and have a direct impact on the attack surface.

---

## Task 3 — Secrets Scanning with detect-secrets

```bash
pip install detect-secrets --break-system-packages
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
detect-secrets scan --baseline .secrets.baseline
```

Baseline creation is a one-time operation that marks existing findings. Explain in your report: what happens if you add a new secret after the baseline is committed? What does the CI check catch that the baseline does not?

For any false positives in the baseline: document the justification. "This is not a secret" is not a sufficient justification — explain what the string is and why it poses no risk if exposed.

---

## Task 4 — Dependency Response Playbook

Write a one-page playbook your team would actually use when a new CVE lands in a dependency. It must cover: who is responsible for triage, what information is needed to make the severity decision, what actions are taken at each severity level, and how exceptions are documented when immediate patching is not possible.

The playbook should reflect the SCSP remediation SLA from Lab 7.6. If the SLA says HIGH must be fixed within 7 days, the playbook must say what happens on day 1, day 3, and day 7.

---

## Discussion

1. pip-audit finds a CRITICAL CVE in a package that CODING WAR uses, but the vulnerable function is only called in a deprecated admin endpoint that will be removed next sprint. What is the correct response — patch now, or wait?

2. Trivy finds that your base image `python:3.11-slim` has 15 MEDIUM OS CVEs. Rebuilding the image with a newer digest would take 2 hours of CI time. What criteria determine whether this is worth doing now versus scheduling for next sprint?

3. `detect-secrets` requires maintaining a `.secrets.baseline` file in the repository. What is the risk of this file itself being misused or becoming stale?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| pip-audit findings + SBOM | **25** | Each CVE assessed for exploitability in CODING WAR context; cross-reference with Lab 7.5 documented |
| Trivy container scan | **25** | Findings triaged against actual deployment; Dockerfile misconfigs identified and prioritised |
| detect-secrets scan | **25** | Baseline created; false positives justified with specific reasoning; CI integration described |
| Dependency response playbook | **15** | Day-by-day actions defined; reflects Lab 7.6 SCSP SLA |
| Discussion | **10** | Answers show practical judgment about real trade-offs |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.4.md](../solutions/sol-8.4.md) after completing the lab.*
