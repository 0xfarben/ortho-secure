# MANAGING SECURITY ACROSS MULTIPLE ENVIRONMENTS WITH DEVSECOPS

This project demonstrates a full-stack **DevSecOps** workflow for a Python web application and MySQL database, managed with Docker, Kubernetes, ArgoCD, and GitLab CI/CD. It includes secure secret management, automated vulnerability scanning, GitOps-based deployment, and monitoring with Prometheus and Grafana.

<img src="app/static/img/icon/icon.png" alt="orthosecure-logo-icon" width="20"/> **Orthosecure: Secure, Modern Dental Practice Management**
---

**Orthosecure** is a fully responsive, full-stack web application designed to streamline dentistry appointment bookings, enhance administrative workflows, and improve patient engagement. With its user-friendly interface and powerful administrative panel, Orthosecure empowers dental practices to efficiently manage appointments, patient records, and clinic operations.

OrthoSecure is a robust and secure application designed to enhance security and compliance within containerized environments. It leverages cutting-edge technologies to monitor, analyze, and secure workloads in real-time.

---

## Features

- **Appointment Booking System:** Allows patients to book, modify, or cancel appointments online with ease.
- **Admin Panel:** Provides clinic administrators with full control over scheduling, patient records, and appointment history.
- **User Authentication:** Secure patient and admin login with session-based management.
- **Responsive Design:** Ensures seamless usability across all devices, including desktops, tablets, and mobile phones.
- **Container Security:** Implements security best practices to safeguard Docker-based environments.
- **Automated Scanning:** Uses SonarQube and other tools for vulnerability detection.
- **CI/CD Integration:** Seamless integration with GitLab CI/CD pipeline.
- **Ease of Deployment:** Simple setup with Docker and Kubernetes.
- **Policy Enforcement:** Implements security policies using Falco and other monitoring tools.

---

## Getting Started

### For End Users

1. **Visit the Application:**
   - Go to [https://orthosecure.work.gd](https://orthosecure.work.gd)
   - Book, modify, or cancel appointments online.
   - Log in as a patient.

2. **No installation required!**
   - All you need is a web browser.

---

### For Developers (Docker Users)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/0xfarben/ortho-secure.git
   cd ortho-secure
   ```
2. **Copy and fill in your environment variables:**
   ```sh
   cp .env.example .env
   # Edit .env and fill in your values
   ```
3. **Start the application locally:**
   ```sh
   docker-compose up --build
   ```
4. **Access the app locally:**
   - [http://localhost:5000](http://localhost:5000)

---

## CI/CD Pipeline (How It Works)

<br>
```sh
Gitlab Link (SCM for this project) -> https://gitlab.com/nidith/ortho-secure
```
<br>

![Architecture](https://raw.githubusercontent.com/0xfarben/ortho-secure/main/Architecture.drawio.svg)
<br>

<center>The pipeline is fully automated and ensures security, code quality, and safe deployment at every step: </center>

<br>

<img src="https://iili.io/FNarLlt.png" alt="ci-cd-pipeline-successful-pipeline-img" border="0">

<br>


1. **Setup Stage:**
   - Installs all Python dependencies and tools in a virtual environment for consistent builds.

   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNcHW2s.png" alt="setup-dependencies-stage-pipeline-img" border="0">
   </details>

2. **Lint Stage:**
   - Checks code formatting and style using Black to enforce code quality and consistency.
   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNlcozv.png" alt="black-lint-stage-pipeline-img" border="0">
   </details>

3. **Security Stage:**
   - Runs Bandit for static security analysis (SAST) to catch common Python security issues early.
   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNl0ARn.png" alt="bandit-security-stage-pipeline-img" border="0">
   </details>

4. **Test Stage:**
   - Runs unit tests with pytest and collects code coverage reports to ensure your code works as expected.
   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNlENcB.png" alt="test-stage-pipeline-img" border="0">
   </details>

5. **SonarQube Stage:**
   - Analyzes code quality and coverage using SonarQube, providing detailed feedback on maintainability and security.
   - Sonarqube got passed with 0 issues, 0 secuirty hotspots(some manually reviewed), got 87.2% code coverage & 0 duplication lines.

   <img src="https://iili.io/FNElne9.png" alt="sonarqube-scanned-result" border="0">

   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNlhEAB.png" alt="sonarqube-check-stage-pipeline-img" border="0">
   </details>

6. **Build Stage:**
   - Builds Docker images for the app and database, tagging them with the commit SHA for traceability.
   - Pushes the images to Docker Hub.
   - Cleans up old images on the build server to save space.
   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNlO6I2.png" alt="build-stage-pipeline-img" border="0">
   </details>

7. **Scan Stage:**
   - Scans the built Docker images for critical vulnerabilities using Trivy.
   - If any critical vulnerabilities are found, the pipeline fails and deployment is blocked.
   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNl8V4t.png" alt="scan-stage-pipeline-img" border="0">
   </details>

8. **Deploy Stage:**
   - If the scan passes, updates the Kubernetes manifests with the new image tags and pushes these changes to the Git repository (with `[ci skip]` to avoid pipeline loops).
   - ArgoCD detects the manifest change and automatically syncs the deployment to your Kubernetes cluster.

   <img src="https://iili.io/FNVNFcP.png" alt="argocd-application-dashboard" border="0">

   - <details>
      <summary>Click to view the pipeline job</summary>
      <img src="https://iili.io/FNlguG2.png" alt="deploy-stage-pipeline-img" border="0">
   </details>

**This pipeline ensures that only secure, tested, and high-quality code is deployed to production, and that all changes are auditable and traceable.**

---

## Monitoring & Observability

- **Prometheus & Grafana:** Deployed via Helm (`kube-prometheus-stack`).
- **Dashboards:** Access Grafana at [https://grafana.orthosecure.work.gd](https://grafana.orthosecure.work.gd) (anonymous view-only).
- **Metrics:** Cluster, pod, and app metrics are collected and visualized.
- **Alerting:** Configure alerts in Prometheus/Grafana as needed.

---

## License

MIT License

Copyright (c) 2024-2025 OrthoSecure

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Contributors

1.  **[Mohammad Thayeeb Shareef](https://github.com/thayeeb9211)**      **[Linkedin Link](https://www.linkedin.com/in/mohammed-thayeeb-shariff-2b614b2b2)**
2.  **[Ramachandragowda S Patil](https://github.com/Ram-82)**       **[Linkedin Link](https://www.linkedin.com/in/ramachandragowda-s-p-b9706a228/)**
3.  **[Satish Biradar](https://github.com/satishbiradar0099)**      **[Linkedin Link](https://www.linkedin.com/in/satish-biradar-38023a284/)**

---


## Acknowledgments

- [Prometheus Community Helm Charts](https://github.com/prometheus-community/helm-charts)
- [ArgoCD](https://argo-cd.readthedocs.io/)
- [Trivy](https://github.com/aquasecurity/trivy)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Kubernetes](https://kubernetes.io/)
- [Docker](https://www.docker.com/)
- [Flask](https://flask.palletsprojects.com/)

---

## ⭐ Support the Project

If you found this helpful, consider starring ⭐ the repository and sharing it with your network! 🚀
