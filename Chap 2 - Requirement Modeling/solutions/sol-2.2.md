# Solution 2.2 — Requirements Modeling (3 Views)

> [!WARNING]
> **Reference Solution** — Complete the lab independently before consulting this.

---

## Discussion Question Answers

**Q1: `«include»` vs `«extend»` for auto-judging:**
`«include»` is correct. Auto-judging is not optional — every submission triggers the judging pipeline. `«extend»` would imply judging is an optional extension that happens under specific conditions. Since judging is always triggered by a submission (it is the point of submission), `«include»` is semantically correct: "Submit Solution" always includes "Run Auto-Judging".

**Q2: Contest ↔ Problem multiplicity and relationship type:**
This is an **Association** (not Aggregation/Composition) because Problems can exist independently of any Contest — they exist in the problem bank first. The multiplicity is many-to-many: a Contest has many Problems (`1..*`), and a Problem can appear in many Contests (`0..*`). This implies a junction entity (e.g., `ContestProblem`) that records which problems are in which contest, and in what order, with what problem letter (A, B, C...).

**Q3: `CE` state and resubmission:**
The `CE` (Compilation Error) state is terminal for that specific submission — it cannot transition to any other verdict. However, the **user** can submit a new, corrected solution (creating a new Submission entity in the `Queued` state). This means the State Machine must show `CE` as a final state with no outgoing transitions, and the system must not "retry" a CE submission automatically — the user must resubmit.

---

## State Machine Key Decisions

**Submission State Machine — critical insight:** `CE` is reached during the `Compiling` state. `RE`, `TLE`, `MLE`, `WA` are all reached during the `Running` state (after successful compilation). `AC` is reached after all test cases pass. Each verdict is a terminal state.

**Contest State Machine — critical insight:** The `Frozen` state does not mean the contest has stopped — contestants can still submit and the scoreboard is still being updated internally. Only the public display is frozen. The transition from `Running` to `Frozen` is triggered by `freeze_time` being reached. The transition from `Frozen` to `Ended` is triggered by `end_time`.

**User Account State Machine — critical insight:** There are two types of "locked": `Locked (Automatic)` triggered by failed login attempts (temporary, self-unlocking after lockout_duration), and `Banned` triggered by Admin action (permanent until Admin reverses it). These must be distinct states with different transitions.

*Back to the lab: [labs/lab-2.2.md](../labs/lab-2.2.md)*
