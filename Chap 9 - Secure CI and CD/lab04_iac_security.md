# Lab 4: Infrastructure as Code (IaC) Security & Policy as Code
**Book:** Bake Security into Modern Software Development
**Chapter 9:** Secure Continuous Integration/Continuous Delivery

## Introduction

In 2019, Capital One suffered a massive data breach exposing over 100 million customer records — the root cause was a misconfigured AWS WAF and overly permissive IAM roles. Had the infrastructure been defined as code and scanned before deployment, the misconfiguration would have been caught before it reached production. Infrastructure misconfigurations are now the #1 cause of cloud security breaches according to Gartner.

This lab brings the Shift-Left principle to infrastructure: instead of auditing cloud resources after provisioning, you will scan Terraform files for security violations **before** `terraform apply` ever runs. This connects to Chapter 9's coverage of IaC Security (Section 4) and Policy as Code, where infrastructure definitions are treated as first-class code artifacts subject to the same security gates as application code.

The CIA Triad applies directly: a publicly accessible S3 bucket violates **Confidentiality**, an overly permissive security group threatens **Availability** (attack surface for DDoS), and deploying unreviewed infrastructure changes undermines **Integrity** of the production environment. Tools like Checkov catch these issues automatically, while Conftest enables custom organizational policies — ensuring compliance is enforced as code, not as a manual checklist.

## 1. Objective
Practice scanning configuration vulnerabilities in infrastructure code (IaC) and applying Policy as Code to prevent the deployment of insecure infrastructure.

**Key skills:**
*   Using Terraform (basics).
*   Scanning IaC with Checkov/Trivy.
*   Writing simple policies with OPA (Open Policy Agent) or Conftest.

## 2. Prerequisites
*   A repository containing Terraform files (`.tf`) or Kubernetes manifests (`.yaml`).
*   The `checkov` tool (can be run via Docker or pip).

### Getting Started
If you haven't completed Lab 1, download the starter project and set up your own repository:
1.  Download the starter code from: https://github.com/sonnt5/Baked-Sec-Secure-SDLC-E01-KDP/tree/main/Labworks/Chap%209%20-%20Secure%20CI%20and%20CD/secure-ci-lab
2.  Create a **new repository** on your GitHub account and push the starter code (see Lab 1, Getting Started for detailed steps).

## 3. Scenario
You are defining AWS infrastructure using Terraform. An engineer on your team has submitted a Pull Request containing an S3 Bucket configured with `public-read` ACL and a Security Group that allows **all inbound traffic from any IP** (`0.0.0.0/0`). Without IaC scanning, these misconfigurations would pass code review (most developers are not cloud security experts) and get applied to production — creating a publicly accessible data store and an attack surface open to the entire Internet.

Your task is to: (1) integrate **Checkov** into the CI pipeline to automatically detect and block common IaC misconfigurations, and (2) write a custom **Conftest/OPA policy** to enforce an organizational rule ("every S3 bucket must have a `CostCenter` tag") that generic scanners do not cover. After completing this lab, insecure infrastructure code will fail the pipeline just like insecure application code.

## 4. Step-by-step Instructions

### Step 1: Create a Terraform File with Misconfigurations
Create an `infra/` directory and a `main.tf` file:

```hcl
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-sensitive-data-bucket"
  acl    = "public-read" # SECURITY FLAW: Allows anyone to read

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Allow all inbound traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # SECURITY FLAW: Opens all ports to the Internet
  }
}
```

### Step 2: Integrate Checkov into the Pipeline
Add an `iac-scan` job to `.github/workflows/ci.yml`:

```yaml
  iac-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Checkov action
        uses: bridgecrewio/checkov-action@master
        with:
          directory: infra/
          quiet: true # Only show errors
          soft_fail: false # Fail pipeline if issues are found
```

### Step 3: Observe the Results
1.  Commit and push the `main.tf` file and the updated workflow.
2.  The pipeline will run and **FAIL** at the Checkov step.
3.  Review the logs — Checkov will clearly identify the misconfigurations.

> **Expected Output:** The Checkov step will produce a report similar to:
> ```
> Passed checks: 2, Failed checks: 4, Skipped checks: 0
>
> Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
>   FAILED for resource: aws_s3_bucket.data_bucket
>   File: /infra/main.tf:1-9
>
> Check: CKV_AWS_19: "Ensure the S3 bucket has server-side-encryption enabled"
>   FAILED for resource: aws_s3_bucket.data_bucket
>   File: /infra/main.tf:1-9
>
> Check: CKV_AWS_20: "Ensure the S3 Bucket has an ACL defined which allows public access"
>   FAILED for resource: aws_s3_bucket.data_bucket
>   File: /infra/main.tf:1-9
>   Guide: https://docs.bridgecrew.io/docs/s3_1-acl-read-permissions-everyone
>
> Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
>   FAILED for resource: aws_security_group.allow_all
>   File: /infra/main.tf:11-21
>   Guide: https://docs.bridgecrew.io/docs/networking_1-port-security
>
> Error: Process completed with exit code 1.
> ```

### Step 4: Remediation
Fix the `main.tf` file:
```hcl
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-sensitive-data-bucket"
  acl    = "private" # Fixed to private
  # ...
}
# ... fix or remove the security group rule ...
```
Commit and push again. The pipeline will turn green.

> **Expected Output:** After fixing, Checkov will show:
> ```
> Passed checks: 6, Failed checks: 0, Skipped checks: 0
> ```

### Step 5: (Advanced) Policy as Code with Conftest
Suppose the company has a rule: "Every S3 Bucket must have a `CostCenter` tag." Checkov may not catch this by default (since it is a custom policy). We use Conftest (based on OPA).

1.  Create a policy file `policy/s3.rego`:
```rego
package main

deny[msg] {
  resource := input.resource.aws_s3_bucket[name]
  not resource.tags.CostCenter
  msg = sprintf("S3 bucket '%v' must have a 'CostCenter' tag", [name])
}
```
2.  Install and run Conftest locally (or add it to CI):
    *   First convert Terraform to JSON: `terraform init && terraform plan -out=tfplan && terraform show -json tfplan > tfplan.json`
    *   Run Conftest: `conftest test tfplan.json -p policy/`
3.  If the tag is missing, this command will return exit code 1 and report an error.

> **Expected Output (Conftest - Missing Tag):**
> ```
> $ conftest test tfplan.json -p policy/
> FAIL - tfplan.json - main - S3 bucket 'data_bucket' must have a 'CostCenter' tag
>
> 1 test, 0 passed, 0 warnings, 1 failure
> ```
>
> **Expected Output (Conftest - Tag Present):**
> After adding `CostCenter = "Engineering"` to the tags block:
> ```
> $ conftest test tfplan.json -p policy/
>
> 1 test, 1 passed, 0 warnings, 0 failures
> ```

## 5. What You Learned

*   **IaC Security scanning** (Checkov) catches common cloud misconfigurations — public S3 buckets, open security groups, missing encryption — before they are deployed, applying the Shift-Left principle to infrastructure.
*   **Policy as Code** (OPA/Conftest) lets you encode custom organizational rules (tagging policies, naming conventions, compliance requirements) as executable code rather than manual checklists.
*   Combining generic scanners (Checkov) with custom policies (Conftest) provides **layered defense**: Checkov catches well-known anti-patterns while Conftest enforces business-specific rules.
*   Infrastructure misconfigurations are the leading cause of cloud breaches — treating Terraform/CloudFormation as security-critical code with mandatory CI gates is essential for maintaining the CIA Triad in cloud environments.
*   The **remediation loop** (fail -> fix -> re-scan -> pass) mirrors the same pattern used for application security gates in Labs 1-2, reinforcing that infrastructure and application code deserve equal security scrutiny.

## 6. Answer Key / Solution Repository
- **Solution branch:** [`chap9-solution`](https://github.com/sonnt5/Baked-Sec-Secure-SDLC-E01-KDP/tree/chap9-solution/Labworks/Chap%209%20-%20Secure%20CI%20and%20CD/secure-ci-lab) — base project to build upon
- Add the `infra/main.tf`, `policy/s3.rego`, and `iac-scan` job to `ci.yml` as described in the steps above
- **Vulnerable state:** Use `acl = "public-read"` and `cidr_blocks = ["0.0.0.0/0"]` in `main.tf` to trigger Checkov failures
- **Fixed state:** Change to `acl = "private"` and restrict security group ingress to pass all gates
