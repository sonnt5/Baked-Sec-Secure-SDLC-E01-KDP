# Solution 2.1 — Stakeholder Analysis & Requirements Elicitation

> [!WARNING]
> **Reference Solution** — Complete the lab independently before consulting this.

---

## Key Points

### Stakeholder Register (sample — not exhaustive)

| Stakeholder | BABOK Role | Power | Interest | Engagement Strategy |
|-------------|-----------|-------|----------|---------------------|
| Head of IT Department | Customer / Sponsor | High | High | Manage closely — key decisions |
| Instructors / Problem Setters | Domain SME + End User | Medium | High | Keep informed and involved |
| Contestants (students) | End User | Low | High | Keep informed via demo |
| System Admin | Operational Support | Medium | High | Consult regularly |
| IT Infrastructure team | Implementation SME | Medium | Medium | Keep informed |
| University management | Sponsor (indirect) | High | Low | Monitor — major issues only |
| Judge Engine (system) | Secondary system actor | N/A | N/A | Technical interface to document |
| Email Service (system) | Secondary system actor | N/A | N/A | Technical interface to document |

**Power/Interest Grid:** High power + High interest → Manage Closely. High power + Low interest → Keep Satisfied. Low power + High interest → Keep Informed. Low power + Low interest → Monitor.

---

### Common Implicit Requirements (often missed)

These are implied by the Customer Brief but not explicitly stated:

- The sandbox must enforce memory limits (implied by MLE verdict)
- The sandbox must enforce CPU time limits (implied by TLE verdict)
- The sandbox must block network access (implied by "cannot affect server")
- The system must support Markdown rendering for problem statements (stated, but students often miss the LaTeX rendering requirement as a separate FR)
- Submission history must be user-specific (implied by privacy — users should only see their own submissions)
- The `freeze_time` for scoreboard must be configurable per contest (implied by Contest Management section)
- Contest Organisers cannot make their own problems Public — Admin approval required (implicit from "only Admin may transition Draft→Public")

---

### Gap Analysis — Key Gaps

**Forward gaps (in Brief but not in User Stories):**
- Account lockout after failed login (Brief section 3.1 — US02 partially covers this, but the Brief implies admin-forced lock as well)
- Admin ability to kick/ban contestants from a contest (Contest section)
- Dry Run requirement before contest goes public
- Partial scoring (mentioned in Judging section — no User Story explicitly covers it)

**Backward gaps (in User Stories but not in Brief):**
- US-02 Acceptance Criteria specifies "lock 15 minutes after 5 failed attempts" — the Brief says "temporarily locked for a period of time" without specifics
- US-08 Acceptance Criteria specifies real-time status updates via WebSocket or Server-Sent Events — the Brief says "real-time" but does not specify the technology

---

### Strong Clarification Question Examples

> "The Customer Brief says the account should be 'temporarily locked' after multiple wrong password attempts. US02 specifies 15 minutes after 5 attempts. Should the lockout be triggered per IP address, per account, or both? If per account, should a logged-in Admin be able to manually unlock accounts?"

> "The Brief says contest submissions cannot see the editorial 'during the contest'. Does this restriction lift immediately at `end_time`, or is there a separate `editorial_publish_time` that Contest Organisers can configure?"

*Back to the lab: [labs/lab-2.1.md](../labs/lab-2.1.md)*
