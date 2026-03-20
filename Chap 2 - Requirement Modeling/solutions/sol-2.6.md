# Solution 2.6 — Security Requirements Elicitation

> [!WARNING]
> **Reference Solution** — Complete the lab independently before consulting this.

---

## Sample Security NFRs (partial — not exhaustive)

```
[NFR-SEC-001] [Critical] Authentication
The system shall store all user passwords using Argon2id with minimum 
parameters: memory_cost = 65536 KB, time_cost = 3, parallelism = 4.
CIA/AAA: Confidentiality / Authentication
Acceptance Criteria: DB scan shows no plaintext passwords; Argon2 config 
  verified in CI; GPU-based crack attempt on sample of 10k hashes fails 
  within 24 hours.

[NFR-SEC-002] [Critical] Authentication
The system shall lock a user account for 15 minutes after 5 consecutive 
failed login attempts from any IP address. Lock duration resets on each 
additional failed attempt.
CIA/AAA: Authentication / Availability
Acceptance Criteria: 6th consecutive failed login returns HTTP 429 with 
  Retry-After header; account accessible after 15 minutes with correct 
  credentials; brute-force simulation of 100 attempts returns 429 
  after attempt #5.

[NFR-SEC-003] [Critical] Sandbox
The system shall execute all contestant-submitted code within a gVisor 
or equivalent kernel-level sandbox. The sandboxed process shall have:
  - No read/write access outside /sandbox/work
  - No outbound network connections  
  - CPU hard cap = problem time_limit + 2 seconds
  - Memory hard cap = problem memory_limit + 32 MB
CIA/AAA: Integrity / Availability
Acceptance Criteria: Submission attempting file-system access outside 
  /sandbox/work receives RE. Submission attempting network connection 
  receives RE. Fork bomb terminates within 5s without host impact.

[NFR-SEC-004] [High] Data Protection
All HTTP communication between clients and the system shall use TLS 1.2 
or higher. HTTP requests shall be automatically redirected to HTTPS.
CIA/AAA: Confidentiality
Acceptance Criteria: TLS scan (e.g., testssl.sh) shows no TLS < 1.2; 
  HTTP request to port 80 returns HTTP 301 to HTTPS.

[NFR-SEC-005] [High] Authorization
The system shall enforce role-based access control. A contestant 
shall not be able to access any submission belonging to another user, 
regardless of the submission ID format.
CIA/AAA: Authorization
Acceptance Criteria: Penetration test — authenticated as User A, 
  attempt to GET /api/submissions/{id_belonging_to_user_B} returns HTTP 403.
```

---

## Discussion Question Answers

**Q1 (security framework is insufficient):**
Security frameworks handle generic patterns (e.g., SQL injection prevention, XSS escaping). But CODING WAR has domain-specific security requirements that no framework can handle automatically:
1. **Sandbox isolation:** No web framework automatically sandboxes user-submitted code with gVisor. This requires infrastructure-level design decisions that must be captured in requirements and architecture.
2. **Scoreboard freeze:** This is a business logic security control — preventing real-time score visibility during the final minutes of a contest. No framework knows when to freeze and unfreeze it; this must be explicitly designed.

**Q2 (Argon2id and password reset):**
If passwords are hashed with Argon2id (one-way, non-reversible), "forgot password" cannot decrypt and show the old password. The only correct design is a **time-limited, single-use reset token**: generate a cryptographically random token, store its hash in the database with an expiry time, email the user a link containing the token, validate the token, then allow the user to set a new password. This is not a constraint — it is the correct design implied by the one-way hashing requirement. The Business Rule would be: "BR-15: Password reset tokens must be single-use, cryptographically random (≥128 bits of entropy), and expire after 60 minutes."

*Back to the lab: [labs/lab-2.6.md](../labs/lab-2.6.md)*
