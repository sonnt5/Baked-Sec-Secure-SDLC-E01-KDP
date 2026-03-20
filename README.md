# Bake Security into Modern Software Development: Secure SDLC - Labs & Resources

Welcome to the official repository for the practical labs and resources accompanying the Applied Security / Secure SDLC book. This repository contains all the hands-on exercises, reference solutions, security configurations, and sample source code organized by each phase of the Secure Software Development Life Cycle.

## Repository Structure

The content is divided into chapters, aligning with the different phases of the Secure SDLC:

* **[Chap 2 - Requirement Modeling](./Chap%202%20-%20Requirement%20Modeling/)**
    * Focuses on the security requirement gathering and modeling phase.
    * Contains sample documents such as the Software Requirements Specification (SRS), Traceability Matrix, and User Stories for the sample project "Coding War".
* **[Chap 3 - Architecture and Design](./Chap%203%20-%20Architecture%20and%20Design/)**
    * Labs and solutions for designing secure system architectures.
* **[Chap 4 - Threat Modeling](./Chap%204%20-%20Threat%20Modeling/)**
    * Guides on identifying and modeling application threats through practical exercises.
* **[Chap 5 - Mitigation, Cryptography and Security Patterns](./Chap%205%20-%20Mitigation,%20Cryptography%20%20and%20Security%20Patterns/)**
    * Risk mitigation strategies, applied cryptography, and security design patterns.
* **[Chap 6 - Security Design Review](./Chap%206%20-%20Security%20Design%20Review/)**
    * Practices for evaluating and reviewing security designs before entering the implementation phase.
* **[Chap 7 - Secure Coding](./Chap%207%20-%20Secure%20Coding/)**
    * Provides source code containing vulnerabilities (`code/vulnerable/`) and their remediated versions (`code/fixed/`).
    * Includes custom rules for the Semgrep static analysis tool.
* **[Chap 8 - Secure Testing](./Chap%208%20-%20Secure%20Testing/)**
    * Hands-on security testing: Includes automated testing, fuzzing (`fuzz_submission.py`), and specific security tests (Authentication, Authorization, Crypto, Input Validation, etc.).
    * Provides configuration files for popular tools like Trivy and OWASP ZAP.
* **[Chap 9 - Secure CI and CD](./Chap%209%20-%20Secure%20CI%20and%20CD/)**
    * Integrating security into the Continuous Integration/Continuous Deployment (CI/CD) pipeline.
    * Contains labs on secure pipeline setup, SCA (Software Composition Analysis) remediation, artifact integrity, and Infrastructure as Code (IaC) security.

## How to Use This Repository

Each chapter contains its own `README.md` file with detailed instructions. To get started:

1.  **Read the Theory and Requirements**: Navigate to the `labs/` directory of each chapter to view the exercises.
2.  **Practice with Source Code**: For programming-related chapters (Chapters 7, 8, and 9), go to the `code/` or `secure-ci-lab/` directories to work directly with configuration files and Python/Node.js scripts.
3.  **Check Your Work**: Once you have completed an exercise, you can compare your approach with the reference implementations in the corresponding `solutions/` directory.

## Disclaimer
The source code in the `vulnerable` directories contains real security flaws and is provided strictly for educational purposes. **Do not use these code snippets in production environments.**