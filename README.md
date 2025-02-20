# OrthoSecure

## Overview
OrthoSecure is a robust and secure application designed to enhance security and compliance within containerized environments. It leverages cutting-edge technologies to monitor, analyze, and secure workloads in real-time.

## Features
- **Container Security:** Implements security best practices to safeguard Docker-based environments.
- **Automated Scanning:** Uses SonarQube and other tools for vulnerability detection.
- **CI/CD Integration:** Seamless integration with GitLab CI/CD pipeline.
- **Ease of Deployment:** Simple setup with Docker and Kubernetes.
- **Policy Enforcement:** Implements security policies using Falco and other monitoring tools.

## Contributors

This project was Contributed by 

1.  **[Nidith VS](https://github.com/0xfarben)**
2.  **[Ramachandragowda S Patil](https://github.com/Ram-82)**
3.  **[Satish Biradar](https://github.com/thayeeb9211/)**
   
# What is DevSecOps 
DevSecOps focuses on security automation, testing and enforcement during DevOps - Release - SDLC cycles. The whole meaning behind this methodology is connecting together Development, Security and Operations. DevSecOps is methodology providing different methods, techniques and processes backed mainly with tooling focusing on developer / security experience. 

DevSecOps takes care that security is part of every stage of DevOps loop - Plan, Code, Build, Test, Release, Deploy, Operate, Monitor. 

Various definitions: 
* https://www.redhat.com/en/topics/devops/what-is-devsecops
* https://www.ibm.com/cloud/learn/devsecops 
* https://snyk.io/series/devsecops/ 
* https://www.synopsys.com/glossary/what-is-devsecops.html
* https://spacelift.io/blog/what-is-devsecops
  
## DevSecOps Archictecture

![DEVSECOPS](https://github.com/user-attachments/assets/784174bd-d668-409a-9f77-14a1b5cf9fd4)

## Getting Started
### Prerequisites
Ensure you have the following installed:
- Docker & Docker Compose
- Git, GitLab Account
- Python 3.11 and JAVA JDK 17 
- SonarQube & Sonar-Scanner (for static code analysis)
- AWS Account and CLI configured
- Terraform CLI configured

### Installation
1. Clone the repository:
   ```sh![download](https://github.com/user-attachments/assets/e81651ca-dc07-43b6-add0-174718a46da6)

   git clone https://your-repository-url.git
   cd orthosecure-main
   ```
2. Set up environment variables:
   ```sh
   cp .env.example .env
   nano .env  # Edit variables as needed
   ```
3. Start the application on Docker:
   ```sh
   ./execute.sh
   ```
4. Run security code scans:
   ```sh
    By Running bandit -r in the Currect directory.
   ```
4. Run SAST scans by ensuring it has sonarsacnner [properties configured]:
   ```sh
   make sure your Sonar Scanner confi properties are like this -- >
     sonar.projectKey=nidith_orthosecure_03ac60c4-e7f9-4f33-b330-4f90a86cc655
     sonar.token=<your sonarqube token>
     sonar.sources=.
     sonar.qualitygate.wait=true
     sonar.host.url=http://localhost:9000/ # Use proper HTTP url
     sonar.python.version=3.11

     if u are not getting how to do it, you can read the PHASE 4 Document in the Reports/ folder
   
    For a SAST Security check run sonar-scanner in the root directory.
   ```

## CI/CD Integration
OrthoSecure integrates with GitLab CI/CD using `.gitlab-ci.yml`, ensuring continuous security analysis and compliance checks.

## Contributing
We welcome contributions! Please follow our guidelines:
- Fork the repository.
- Create a new branch (`feature/your-feature`).
- Commit changes and push to GitHub.
- Submit a pull request.


## 🛠️ Author & Community  

This project is crafted by **[Mohammed Thayeeb Shariff](https://github.com/thayeeb9211/)** 💡 
I’d love to hear your feedback! Feel free to share your thoughts.  
   
📧 **Connect with me:**

- **LinkedIn**: [Mohammed Thayeeb Shariff](https://www.linkedin.com/in/mohammed-thayeeb-shariff-2b614b2b2/)  

---

## ⭐ Support the Project  

If you found this helpful, consider **starring** ⭐ the repository and sharing it with your network! 🚀  

### 📢 Stay Connected  

https://data-driven-portfolio-s3q1onv.gamma.site/

---
**OrthoSecure - Securing Containers, Simplifying Security.** 🚀

## License
This project is licensed under the terms specified in the `LICENSE` file.
