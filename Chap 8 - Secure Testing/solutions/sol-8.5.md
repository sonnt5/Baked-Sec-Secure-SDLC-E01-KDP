# Solution 8.5 — IaC Security: Trivy + Checkov

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### Judge worker vs API server — the critical distinction

The API server handles HTTP requests. The judge worker executes arbitrary user-submitted code. The threat model for these two pods is completely different. For the API server, `privileged: false` and `readOnlyRootFilesystem: true` are straightforward improvements. For the judge worker, you must understand exactly which capabilities gVisor requires before dropping them — removing a required capability causes judge worker crashes, which is a DoS against the contest.

The minimum capability set for gVisor (`runsc`) typically requires: none from the host perspective if using the Kubernetes RuntimeClass; the containment is provided by the gVisor kernel, not by Linux capabilities. Document which capabilities your deployment actually needs by testing with an increasingly restricted set.

### The three highest-priority findings

1. **`runAsNonRoot: false` on judge worker** — executing as root inside a container that runs user code means a container escape gives root on the host. This is the highest-priority finding.

2. **No resource limits** — a contestant who submits a fork bomb or memory-exhausting code can bring down the entire node if no limits are set. This is a DoS finding that directly threatens contest availability.

3. **`FROM python:3.11-slim` (unpinned tag)** — `docker pull` on the same tag can return different images on different days. A compromised or updated image silently affects all future builds. Pin to SHA256 digest.

### Fix for resource limits — rationale for values

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "1000m"
    memory: "512Mi"
```

The gap between requests and limits allows burst handling. Kubernetes schedules based on requests; limits are enforced by the cgroup. For the judge worker, limits should be lower — the sandbox's own resource limits (time and memory) should fire before the pod limit, to ensure verdicts are correct rather than the pod being OOM-killed.

### Discussion answers

**Q1 — Developer adds `privileged: true`:** Block the PR and explain why. "Development only" changes in Kubernetes manifests are not safe because manifests are applied to environments, not built into binaries. If the manifest is committed, it may be applied to staging or production by accident. The correct fix is to add a local `kind` override or a dev-specific values file that is gitignored, not to modify the base manifest.

**Q2 — No resource limits for 6 months without incident:** No incidents means no attacker has tried yet, or the attacks that occurred did not cause visible damage. It does not mean the system is resilient. A single malicious submission with a fork bomb would demonstrate the impact immediately. The absence of incidents is not a risk assessment.

**Q3 — `FROM :latest` vs pinning:** The argument is wrong. Pinning to a digest does not prevent getting security patches — it requires you to consciously update the digest when a new patch is released, which is exactly what you want. Automatic tag updates mean you get patches, but you also get regressions, new CVEs introduced by the update, and changes in library versions — all without review. Pin to digest and use Dependabot or Renovate to automate digest update PRs.

---

*Back to the lab: [labs/lab-8.5.md](../labs/lab-8.5.md)*
