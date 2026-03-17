# Solution 2.3 — SRS Document

> [!WARNING]
> **Reference Solution** — Complete the lab independently before consulting this.

---

## Sample Business Rules (not exhaustive)

| BR-ID | Statement | Related UCs |
|-------|-----------|-------------|
| BR-01 | A problem must have at least one test case before it can be transitioned from Draft to Public status. | UC Problem Publish |
| BR-02 | Only Admin may transition a problem from Draft to Public status. | UC Problem Publish |
| BR-03 | A contestant may not view the source code of another contestant's submission during an active contest. | UC View Submission History |
| BR-04 | The Join button for a contest is only active between `start_time` and `end_time`. | UC Join Contest |
| BR-05 | A contest must pass Dry Run (100% of model solutions judged AC) before it can be made Public. | UC Create Contest |
| BR-06 | The scoreboard displays only submissions up to `freeze_time` to contestants; Admin always sees the live scoreboard. | UC View Scoreboard |
| BR-07 | Source code submitted for judging is executed only within the sandboxed Judge Engine environment and has no direct access to the host filesystem, network, or other submissions. | UC Submit Solution |
| BR-08 | An account locked due to failed login attempts is automatically unlocked after `lockout_duration` minutes with no Admin intervention required. | UC Login |
| BR-09 | Submission status updates sequentially: Queued → Compiling → Running → Result. Status may not skip stages. | UC Submit Solution |
| BR-10 | A problem's time limit must be between 100 milliseconds and 10,000 milliseconds. | UC Create Problem |
| BR-11 | Contest problems are visible to contestants only after the contest `start_time`. Before that, the problem list is hidden. | UC Participate in Contest |
| BR-12 | The judging result for a submission is immutable once set — it cannot be changed after the fact, except by Admin through an explicit re-judge action. | UC Submit Solution, UC Admin Re-Judge |

---

## Sample Strong NFR (for reference)

```
[REQ-NFR-003] [Critical] Sandbox Isolation
The system shall execute all contestant-submitted code within an isolated 
sandbox environment (e.g., gVisor, Docker with seccomp profiles) such that:
  - The process has no read/write access to any filesystem path outside 
    its designated working directory.
  - The process cannot establish any outbound or inbound network connections.
  - The process cannot create child processes beyond what is required for 
    single-program execution.
  - The process is subject to hard resource limits: CPU time ≤ problem 
    time_limit + 2 seconds, memory ≤ problem memory_limit + 32 MB.

Acceptance Criteria:
  - Penetration test: a submission that attempts `open('/etc/passwd', 'r')` 
    receives RE (Runtime Error), not file contents.
  - A submission executing `import socket; socket.connect(...)` receives RE.
  - A fork bomb submission receives TLE or MLE within 5 seconds without 
    affecting other concurrent submissions.
```

*Back to the lab: [labs/lab-2.3.md](../labs/lab-2.3.md)*
