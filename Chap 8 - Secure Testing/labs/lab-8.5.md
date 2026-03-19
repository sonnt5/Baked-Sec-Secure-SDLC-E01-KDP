# Lab 8.5 — IaC Security: Trivy + Checkov

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: `k8s/*.yaml` + `Dockerfile` + `docker-compose.yml`
> Output: IaC Scan Report + Prioritised Findings + CI Integration

## Learning Objectives

- Scan Kubernetes manifests and Dockerfiles with Trivy and Checkov.
- Triage IaC misconfigurations against the actual CODING WAR deployment context — not just the generic finding description.
- Understand the security significance of workload isolation controls in a system that executes untrusted code.

## Code Files

| File | Role |
|------|------|
| `code/config/trivy-config.yaml` | Trivy scan configuration |

---

## Task 1 — Trivy IaC Scan

```bash
trivy config --config code/config/trivy-config.yaml .
trivy config k8s/
trivy config Dockerfile
```

For each finding, triage it against the CODING WAR deployment. The judge worker pod has different security requirements than the API server — a capability that is "not needed" for the API server may be required by gVisor for the judge worker. Document the difference.

The highest-priority findings for CODING WAR are those affecting the judge worker pod. Explain why — what is the threat model for a container that executes arbitrary user-submitted code?

---

## Task 2 — Checkov Scan

```bash
pip install checkov --break-system-packages
checkov -d k8s/ --framework kubernetes -o json --output-file checkov-results.json
checkov -f Dockerfile --framework dockerfile
checkov -f docker-compose.yml --framework docker_compose
```

For each Checkov finding: state whether it is a True Positive, False Positive, or N/A for CODING WAR. False Positive and N/A conclusions require technical justification — explain the specific CODING WAR context that makes the finding non-applicable.

Identify the three findings that, if left unaddressed, would most significantly increase the blast radius of a successful exploitation.

---

## Task 3 — Fix Design

For the three highest-priority findings you identified: write the corrected Kubernetes manifest snippet or Dockerfile change. Your fix must be accompanied by a comment in the manifest explaining what it prevents — another engineer reading the YAML should understand the security intent without referring to this lab.

For the judge worker, you will encounter a tension: hardening requirements (read-only filesystem, no privilege escalation, dropped capabilities) conflict with gVisor's runtime requirements. Document which capabilities gVisor actually needs and why, and how you would verify the minimum necessary set.

---

## Task 4 — CI Integration

Write the workflow `steps:` block that adds IaC scanning to the CI pipeline. The scan should run on changes to `k8s/*.yaml`, `Dockerfile`, or `docker-compose.yml`, and also nightly. Findings at CRITICAL and HIGH must block; MEDIUM findings should alert without blocking.

Explain: why does the IaC scan run on a path-triggered condition in addition to the nightly schedule? What class of regression would the nightly-only approach miss?

---

## Discussion

1. A new engineer modifies the judge worker deployment to add `privileged: true` to get their development environment working quickly. The IaC scan catches it and blocks their PR. They argue that this is a development-only change. What is the correct response?

2. You find that your Kubernetes manifests have never specified resource limits and the application has been running in production for 6 months without issue. Does the absence of incidents mean the finding can be deprioritised?

3. Checkov flags `FROM python:3.11-slim` (unpinned tag) as a finding. Your team argues that pinning to a digest would make it harder to get security patches automatically. Evaluate this argument.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Trivy IaC scan triage | **25** | Judge worker vs API server distinction made; findings triaged against deployment context |
| Checkov scan analysis | **25** | Three highest-priority findings identified with reasoning; False Positive/N/A conclusions technically justified |
| Fix design | **30** | Manifests correct; security intent documented in the YAML; gVisor capability tension addressed |
| CI integration | **10** | Path-triggered + nightly; blocking thresholds correct; nightly-only gap explained |
| Discussion | **10** | Answers show practical judgment |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.5.md](../solutions/sol-8.5.md) after completing the lab.*
