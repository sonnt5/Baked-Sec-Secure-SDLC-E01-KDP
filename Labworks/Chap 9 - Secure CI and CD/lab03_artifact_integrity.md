# Lab 3: Ensuring Artifact Integrity (Signing & SBOM)
**Book:** Bake Security into Modern Software Development
**Chapter 9:** Secure Continuous Integration/Continuous Delivery

## Introduction

The SolarWinds SUNBURST attack (2020) was a watershed moment for software supply chain security. Attackers compromised the build system to inject malicious code into signed artifacts — the resulting trojanized update was distributed to over 18,000 organizations, including US government agencies. This attack succeeded because there was no mechanism to verify that the artifact matched the source code or that it had not been tampered with after building.

This lab addresses the **Artifact Integrity and Provenance** concepts from Chapter 9 by implementing the SLSA (Supply-chain Levels for Software Artifacts) framework in practice. You will create a Docker image, generate an SBOM (Software Bill of Materials) to document exactly what is inside the artifact, and apply a digital signature using Cosign/Sigstore to prove its origin and integrity.

These controls map directly to the CIA Triad: the **Integrity** of the artifact is guaranteed by the digital signature, **Confidentiality** of the build identity is managed through OIDC keyless signing, and **Availability** is protected by ensuring only verified artifacts reach production — preventing supply chain attacks from taking down your systems.

## 1. Objective
Practice protecting the supply chain at the packaging stage (Build & Package). You will create a Docker Image, generate an SBOM, and apply a Digital Signature to ensure the artifact has not been tampered with.

**Key skills:**
*   Creating a Dockerfile and Building an Image.
*   Generating an SBOM with Syft/Trivy.
*   Signing artifacts with Cosign (Sigstore).
*   Verifying signatures (Verification).

## 2. Prerequisites
*   A repository with a Dockerfile (will be created in Step 1).
*   A Docker Hub account (or GHCR - GitHub Container Registry).
*   GitHub Actions.

## 3. Scenario
Your company requires that every Docker Image must have an "identity card" (SBOM) and a "seal" (Signature) from the development team before being deployed to Production. Currently, any image pushed to the container registry can be deployed — there is no way to verify **who** built it, **what** is inside it, or whether it was **tampered with** after building. This means a compromised CI runner, a rogue insider, or a man-in-the-middle attack could inject malicious code into a production image without detection.

Your task is to implement a three-layer protection: (1) **SBOM generation** so the contents of every image are documented, (2) **Digital signing** using Cosign with OIDC keyless signing so the image's origin is cryptographically verifiable, and (3) a **Deploy Gate** script that rejects any unsigned image — achieving SLSA Level 2 provenance.

## 4. Step-by-step Instructions

### Step 1: Prepare the Dockerfile
Create a `Dockerfile` at the project root:
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "app.js"]
```

### Step 2: Build, Generate SBOM, and Sign in GitHub Actions
Update the workflow `.github/workflows/ci.yml`. We will use `cosign` (requires the setup-cosign action).
*Note: For simplicity, this lab pushes images to GHCR (GitHub Container Registry).*

```yaml
  build-and-sign:
    needs: [security] # Only runs when security passes
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write # Required for Cosign Keyless signing

    steps:
      - uses: actions/checkout@v3

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3.1.1

      - name: Log in to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Docker image
        id: build-and-push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}/myapp:latest

      - name: Generate SBOM
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'image'
          image-ref: 'ghcr.io/${{ github.repository }}/myapp:latest'
          format: 'cyclonedx'
          output: 'sbom.json'

      - name: Sign the images with GitHub OIDC Token
        env:
          DIGEST: ${{ steps.build-and-push.outputs.digest }}
          TAGS: ghcr.io/${{ github.repository }}/myapp:latest
        run: |
          cosign sign --yes "${TAGS}@${DIGEST}"
          # Also sign the SBOM (Attestation) - Advanced
          cosign attest --yes --predicate sbom.json --type cyclonedx "${TAGS}@${DIGEST}"
```

> **Expected Output:** After the workflow completes, the signing step will produce:
> ```
> Generating ephemeral keys...
> Retrieving signed certificate...
> Successfully verified SCT...
> tlog entry created with index: 12345678
> Pushing signature to: ghcr.io/your-org/your-repo/myapp:sha256-abc123.sig
>
> Generating ephemeral keys...
> Retrieving signed certificate...
> Successfully verified SCT...
> tlog entry created with index: 12345679
> Pushing attestation to: ghcr.io/your-org/your-repo/myapp:sha256-abc123.att
> ```

### Step 3: Verify the Results
1.  Push the code to main.
2.  After the pipeline completes, go to the Repository homepage -> Packages. You will see the new Container image.
3.  To verify the signature, you can install `cosign` on your local machine and run the verify command:

```bash
cosign verify \
  --certificate-identity "https://github.com/<OWNER>/<REPO>/.github/workflows/ci.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/<OWNER>/<REPO>/myapp:latest
```
*(Replace `<OWNER>/<REPO>` with your repository name)*.

> **Expected Output (Verification Success):**
> ```
> Verification for ghcr.io/your-org/your-repo/myapp:latest --
> The following checks were performed on each of these signatures:
>   - The cosign claims were validated
>   - Existence of the claims in the transparency log was verified offline
>   - The code-signing certificate was verified using trusted certificate authority
>
> [{"critical":{"identity":{"docker-reference":"ghcr.io/your-org/your-repo/myapp"},
> "image":{"docker-manifest-digest":"sha256:abc123..."},
> "type":"cosign container image signature"},
> "optional":{"Issuer":"https://token.actions.githubusercontent.com",
> "Subject":"https://github.com/your-org/your-repo/.github/workflows/ci.yml@refs/heads/main"}}]
> ```

### Step 4: Simulate a Deploy Gate
Create a script file `deploy_check.sh` (simulation):
```bash
#!/bin/bash
IMAGE=$1
echo "Checking signature for $IMAGE..."
if cosign verify ... $IMAGE > /dev/null 2>&1; then
  echo "Signature Verified. Deploying..."
else
  echo "Signature Verification FAILED! Deployment Blocked."
  exit 1
fi
```
This demonstrates how a deployment system (like ArgoCD or a Kubernetes Admission Controller) would block images of unknown origin.

> **Expected Output (Deploy Gate - Success):**
> ```
> $ ./deploy_check.sh ghcr.io/your-org/your-repo/myapp:latest
> Checking signature for ghcr.io/your-org/your-repo/myapp:latest...
> Signature Verified. Deploying...
> ```
>
> **Expected Output (Deploy Gate - Failure with unsigned image):**
> ```
> $ ./deploy_check.sh ghcr.io/some-other/unsigned-image:latest
> Checking signature for ghcr.io/some-other/unsigned-image:latest...
> Signature Verification FAILED! Deployment Blocked.
> ```

## 5. What You Learned

*   **SLSA Framework** provides a maturity model for supply chain security — this lab achieves Level 2 by implementing automated builds with signed provenance from a version-controlled pipeline.
*   **Artifact Signing** with Cosign (Sigstore) uses OIDC keyless signing to cryptographically bind a container image to its CI pipeline identity, eliminating the need to manage long-lived signing keys.
*   **SBOM generation** creates a complete inventory of every component inside an artifact, enabling downstream consumers to assess vulnerability exposure and license compliance.
*   A **Deploy Gate** (signature verification) acts as the last checkpoint before production, ensuring only trusted, verified artifacts are deployed — directly supporting the Integrity pillar of the CIA Triad.
*   Combining SBOM + Signing + Verification creates an end-to-end **chain of trust** from source code to production deployment.

## 6. Answer Key / Solution Repository
- **Repository:** https://github.com/maycuatroi1/artifact-integrity-lab
- **`main` branch:** Complete working solution (all security gates pass)
- *Note: This lab does not have a `vulnerable` branch, as the focus is on artifact signing and SBOM generation rather than vulnerability detection.*
