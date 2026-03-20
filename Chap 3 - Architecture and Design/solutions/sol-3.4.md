# Solution 3.4 — Five Views: Deployment Design

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Deployment Diagram (text description)

```
┌─────────────────────────────────────────────────────────────┐
│  Internet / Client Zone                                       │
│  [Browser / Mobile Client]                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTPS :443
┌──────────────────▼──────────────────────────────────────────┐
│  DMZ / Edge Layer                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Nginx Reverse Proxy  :80, :443                      │    │
│  │  (SSL termination, rate limiting)                    │    │
│  └──────────────────────┬──────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP :8000
┌─────────────────────────▼───────────────────────────────────┐
│  Application Layer                                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │  CODING WAR App Server                              │     │
│  │  (Docker: coding-war-api:latest)                    │     │
│  │  FastAPI / Uvicorn  :8000                           │     │
│  └──────────────────────┬─────────────────────────────┘     │
│                          │ AMQP                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  JudgeWorker (separate process)                     │     │
│  │  (Docker: coding-war-judge:latest)                  │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │ TCP/5432      │ TCP/6379      │ AMQP/5672
┌────────▼────────┐  ┌───▼────┐  ┌──────▼──────────────────┐
│ PostgreSQL :5432│  │ Redis  │  │  RabbitMQ :5672/:15672   │
│ (primary DB)    │  │ :6379  │  │  (message broker)        │
└─────────────────┘  └────────┘  └──────────────────────────┘
         │ TCP/9000
┌────────▼─────────────────┐
│  MinIO Object Storage     │
│  :9000  (test case files) │
└───────────────────────────┘
```

> 📎 Recreate this diagram in draw.io or PlantUML and attach the image to your submission.

---

## Task 2 — Infrastructure Decision Table

| Component | Selected | Alternative | Reason for Selection |
|-----------|---------|-------------|----------------------|
| **Web / Reverse Proxy** | **Nginx** | Caddy, AWS ALB | Mature and battle-tested, flexible config, built-in rate limiting and SSL termination. Ideal for self-hosted deployments. |
| **Application Runtime** | **Docker containers** | VMs, bare metal | Reproducible environments, easy deployment, isolation between the API and the JudgeWorker. Aligns with the sandbox isolation NFR. |
| **Primary Database** | **PostgreSQL** | MySQL, MongoDB | Full ACID compliance, strong consistency for scoring. Native UUID support. JSONB columns for flexible schema when needed. |
| **Cache Layer** | **Redis** | Memcached | Redis supports advanced data structures (Sorted Sets for scoreboard rankings), pub/sub, and optional persistence. Memcached is key-value only. |
| **Message Queue** | **RabbitMQ** | Kafka, Redis Streams | RabbitMQ fits CODING WAR's task-queue workload well (no need for long log retention). Kafka would be over-engineered at the current scale. |
| **Sandbox Execution** | **gVisor** | Docker-in-Docker, Firejail | gVisor provides kernel-level isolation without nested Docker (which carries security risks). Firejail is less mature for this use case. |
| **Object Storage** | **MinIO** | AWS S3, Local FS | MinIO is S3-compatible and self-hosted — suitable for on-premise deployment. Easy to migrate to AWS S3 later if needed. |
| **Monitoring** | **Prometheus + Grafana** | ELK, Datadog | Open source with no licensing cost. Prometheus excels at metrics; pair with Loki for logs if needed. |

---

## Task 3 — SPOF Analysis

| Component | SPOF? | Impact if it Fails | Solution |
|-----------|-------|-------------------|---------|
| **Nginx / Load Balancer** | **Y** | All traffic is blocked; system is completely inaccessible | Run 2 Nginx instances with Keepalived/VRRP; or use a managed LB (AWS ALB, GCP LB) with built-in HA |
| **Application server** | **Y** | API unavailable; no submissions possible | Run ≥2 instances behind the load balancer; health checks auto-restart failed instances |
| **PostgreSQL** | **Y** | Complete loss of data persistence; no reads or writes | PostgreSQL Streaming Replication (1 primary + 1 standby); automatic failover with Patroni or pg_auto_failover |
| **RabbitMQ** | **Y** | Submissions not judged; queue messages potentially lost | RabbitMQ Quorum Queues (recommended); ≥3 node cluster |
| **Redis Cache** | **N** (degraded) | Slower scoreboard, more cache misses — but data still exists in PostgreSQL | Redis Sentinel or Redis Cluster for HA; fallback to PostgreSQL reads if Redis fails |
| **JudgeWorker** | **N** (degraded) | Submissions remain in queue, unjudged — but not lost | Run ≥2 JudgeWorker processes; RabbitMQ message persistence ensures no submissions are lost; auto-restart via process supervisor |

---

## Task 4 — Beta → Production Evolution

> **Change 1: Scale JudgeWorker replicas**
> Beta runs a single JudgeWorker. Production (500+ users with many concurrent submissions) requires ≥3–5 workers. RabbitMQ distributes messages automatically. Each worker needs dedicated CPU and memory for sandbox isolation. Monitor queue depth and auto-scale accordingly.

> **Change 2: PostgreSQL Primary-Replica Replication**
> Beta can run on a single PostgreSQL node. Production requires at least one standby replica for: (a) failover when the primary fails, and (b) a read replica to offload read-heavy queries (problem listings, scoreboard history) from the primary. Routing rule: writes go to the primary; read-heavy queries go to the replica.

> **Change 3: Horizontal App Server Scaling + Session Externalization**
> Beta may run a single app server. Production requires ≥2 instances behind Nginx (round-robin load balancing). Requirements: session state must be externalized to Redis (not stored in-memory), and JWT tokens must be stateless. Add PgBouncer for database connection pooling to prevent connection exhaustion when multiple instances are running.

---

*Back to the lab: [labs/lab-3.4.md](../labs/lab-3.4.md)*
