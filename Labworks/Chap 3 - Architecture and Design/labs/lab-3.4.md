# Lab 3.4 — Five Views: Deployment Design

> **Chapter 3 · Software Architecture and Design**
> Input: Output from Lab 3.2 + 3.3 | Output: Deployment diagram, ADR

## Learning Objectives

- Design a Deployment View: map software components to infrastructure nodes.
- Define the deployment topology, network zones, and infrastructure constraints.
- Analyze Single Points of Failure (SPOFs) and propose availability improvements.
- Compare deployment scenarios and select the most appropriate one given the project's constraints.

## Scenario

CODING WAR is preparing for beta launch targeting approximately **200 concurrent users**. The team needs to design an initial deployment topology, then analyze its weaknesses and propose improvements for the production phase targeting **500+ concurrent users** (as defined in the NFRs).

---

## Task 1 — Draw a Deployment Diagram

Design a Deployment Diagram (UML) for CODING WAR. The diagram must show:

- **Execution environments (nodes):** web server, app server, database server, message broker, cache.
- **Artifacts (components)** deployed on each node.
- **Communication paths** between nodes (protocol: HTTP/HTTPS, TCP, AMQP...).
- **External dependencies:** client browsers, external DNS/CDN if applicable.

> 📎 Insert Deployment Diagram here

---

## Task 2 — Infrastructure Decision Table

Complete the infrastructure decision table below:

| Infrastructure Component | Selected Technology | Alternative Considered | Reason for Selection (linked to NFR) |
|--------------------------|--------------------|-----------------------|--------------------------------------|
| **Web / Reverse Proxy** | \[Nginx / Caddy / AWS ALB\] | \[Fill in alternative\] | \[Reason\] |
| **Application Runtime** | \[Docker containers / VMs / bare metal\] | \[Fill in\] | \[Fill in\] |
| **Primary Database** | \[PostgreSQL / MySQL / MongoDB\] | \[Fill in\] | \[Fill in\] |
| **Cache Layer** | \[Redis / Memcached\] | \[Fill in\] | \[Fill in\] |
| **Message Queue** | \[RabbitMQ / Kafka / Redis Streams\] | \[Fill in\] | \[Fill in\] |
| **Sandbox Execution** | \[Docker-in-Docker / gVisor / Firejail\] | \[Fill in\] | \[Fill in\] |
| **Object Storage (test cases)** | \[MinIO / S3 / Local FS\] | \[Fill in\] | \[Fill in\] |
| **Monitoring** | \[Prometheus+Grafana / ELK / Datadog\] | \[Fill in\] | \[Fill in\] |

---

## Task 3 — SPOF Analysis & Availability Improvement

Analyze Single Points of Failure in the deployment topology you designed and propose solutions:

| Component / Node | SPOF? (Y/N) | Impact if it Fails | Proposed Solution to Improve Availability |
|-----------------|------------|-------------------|------------------------------------------|
| **Web server / Load Balancer** | \[Y/N\] | \[Fill in impact severity\] | \[Fill in: redundancy, failover, replication...\] |
| **Application server** | \[Y/N\] | \[Fill in\] | \[Fill in\] |
| **Database server** | \[Y/N\] | \[Fill in\] | \[Fill in\] |
| **Message Queue** | \[Y/N\] | \[Fill in\] | \[Fill in\] |
| **Redis Cache** | \[Y/N\] | \[Fill in\] | \[Fill in\] |
| **Judge sandbox node** | \[Y/N\] | \[Fill in\] | \[Fill in\] |

---

## Task 4 — Design Evolution: Beta → Production

Describe (in prose or bullet points) how the deployment topology will change when the system scales from **Beta (200 users)** to **Production (500+ users)**. Focus on the 3 most important changes:

> **Change 1:** \[Fill in\]
>
> **Change 2:** \[Fill in\]
>
> **Change 3:** \[Fill in\]

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Deployment Diagram — complete and accurate | **35** | All nodes, artifacts, communication paths, and protocols present |
| Infrastructure Decision Table | **25** | Reasons clearly linked to NFRs; alternatives are meaningful |
| SPOF Analysis | **25** | ≥4 SPOFs correctly identified, impact assessment is reasonable, solutions are practical |
| Beta → Production Evolution | **15** | 3 changes analyzed with technical depth |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-3.4.md](../solutions/sol-3.4.md)*
