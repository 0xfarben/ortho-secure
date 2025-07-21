<img src="https://github.com/user-attachments/assets/6a102742-c3ec-4ebd-94be-3672d7f961d0" alt="Shortened Image" width="auto" height="50">  

# OrthoSecure 

## Overview
Orthosecure is a fully responsive, full-stack web application designed to streamline dentistry appointment bookings, enhance administrative workflows, and improve patient engagement. With its user-friendly interface and powerful administrative panel, Orthosecure empowers dental practices to efficiently manage appointments, patient records, and clinic operations.
OrthoSecure is a robust and secure application designed to enhance security and compliance within containerized environments. It leverages cutting-edge technologies to monitor, analyze, and secure workloads in real-time.

![image](https://github.com/user-attachments/assets/994a3399-abe9-4dcd-af57-40e5505c91e9)

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


## Complete Video Demonstration
![Architecture](https://raw.githubusercontent.com/0xfarben/ortho-secure/main/Architecture.drawio.svg)


## Reports folder

we have a dedicated Reports folder which explains the overall project with ease. Make sure you do check it before you proceed.

## Project Team Members

1.  **[Mohammad Thayeeb Shareef](https://github.com/thayeeb9211)**      **[Linkedin Link](https://www.linkedin.com/in/mohammed-thayeeb-shariff-2b614b2b2)**
2.  **[Ramachandragowda S Patil](https://github.com/Ram-82)**       **[Linkedin Link](https://www.linkedin.com/in/ramachandragowda-s-p-b9706a228/)**
3.  **[Satish Biradar](https://github.com/satishbiradar0099)**      **[Linkedin Link](https://www.linkedin.com/in/satish-biradar-38023a284/)**
   
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

# Security-Focused DevSecOps Tool Implementation 🚀

Security is a top priority in this project. Below are the DevSecOps security tools integrated into the development pipeline to ensure code quality, vulnerability detection, and secure infrastructure management.

## 1️⃣ Trivy - Container & Dependency Scanning 🔍

   ![image](https://github.com/user-attachments/assets/e67efc84-350d-4720-bc47-c96dc1406037)
      
      Why it's used?
      Trivy is an open-source vulnerability scanner used to scan Docker images, file systems, and dependencies for security vulnerabilities.
      It provides CVE (Common Vulnerabilities and Exposures) reports to ensure the container images are secure before deployment.
      
      Benefits:
         ✅ Fast and accurate vulnerability scanning.
         ✅ Seamlessly integrates with GitLab CI/CD.
         ✅ Helps maintain compliance and security best practices.

## 2️⃣ SonarQube & Static Code Analysis in GITLAB with Ci/CD 🛠️

### Results of Auto-Enabling the SAST and IaC security Check on GITLAB
   ![image](https://github.com/user-attachments/assets/b916bb90-5248-4208-b0e4-d0f28d252c51)
   ![image](https://github.com/user-attachments/assets/013531a8-5bd4-4e4b-94e2-bba995da995d)
   ![image](https://github.com/user-attachments/assets/f30230f5-98aa-4bde-8000-7a3ae817e2c0)

### Results of SonarQube Dashboard for Scanning full source code
   ![image](https://github.com/user-attachments/assets/11b19c65-6778-4a14-b06e-f3bc43fa418a)

      Why it's used?
      SonarQube is used to perform static code analysis to detect bugs, vulnerabilities, and maintainability issues.
      It helps enforce coding standards and security best practices.
      we have also Auto-enabled it in GITLAB for continous evaluation.
      Benefits:
      ✅ Detects security flaws like SQL injection and XSS.✅ Improves code maintainability and readability.✅ Provides in-depth security insights for developers.

## 3️⃣ Bandit - Python Security Linter 🐍

   ![image](https://github.com/user-attachments/assets/60f2d468-931e-485b-9a59-e92d774b7379)

      Why it's used?
      Bandit is a security linter specifically for Python code, helping identify security vulnerabilities in Python scripts and applications.
      It scans the code for common security issues such as hardcoded passwords and insecure function usage.
      Benefits:
      ✅ Helps catch security flaws early in development.✅ Ensures Python code adheres to security best practices.✅ Integrates easily with CI/CD pipelines for automated checks.

## 4️⃣ Black - Python Code Formatter 🎨

   ![image](https://github.com/user-attachments/assets/a88b702b-5b96-4bfd-ae8d-a3c443fcb733)

      Why it's used?
      Black is an opinionated Python code formatter that ensures consistent and readable code.
      It eliminates syntax-related security issues by enforcing a uniform coding style.
      Benefits:
      ✅ Improves code readability and maintainability.✅ Reduces syntax-related security vulnerabilities.✅ Makes collaboration easier by enforcing a consistent format.

## 5️⃣ Terraform - Infrastructure as Code (IaC) 🏗️

   ![image](https://github.com/user-attachments/assets/19d62bd1-88f0-46d0-b5b8-1d3acaa79e10)
   ![image](https://github.com/user-attachments/assets/b431662a-32fc-473f-9c46-daafa5401444)
   ![image](https://github.com/user-attachments/assets/aaeb7ac0-6e3d-4ea4-9515-29da89f40953)

      Why it's used?
      Terraform is used to manage infrastructure as code, enabling automated deployment and management of cloud resources.
      It ensures reproducibility, consistency, and security in infrastructure provisioning.
      Benefits:
      ✅ Enables version control and automation of infrastructure.✅ Reduces human errors and misconfigurations.✅ Ensures security by enforcing controlled infrastructure deployment.

## 6️⃣ Kubernetes - Container Orchestration ⚡

   ![image](https://github.com/user-attachments/assets/6bbfed54-df88-4745-98f7-dbf03ce23dcd)

      Why it's used?
      Kubernetes manages containerized applications by automating deployment, scaling, and operations.
      It ensures high availability, load balancing, and secure container orchestration.
      Benefits:
      ✅ Efficient container management with automated scaling.✅ Built-in security policies and access controls.✅ Provides resilience and fault tolerance for applications.

## 7️⃣ HashiCorp Vault - Secrets Management 🔑

   ![image](https://github.com/user-attachments/assets/4b4fca20-f47f-4193-8b81-095bdf7d73d3)
   ![image](https://github.com/user-attachments/assets/5c350c60-c7d3-4558-8dc5-9cd9b310342c)

      Why it's used?
      HashiCorp Vault is used for securely storing and managing sensitive data such as API keys, credentials, and certificates.
      It integrates with Kubernetes to inject secrets into containers securely.
      Benefits:
      ✅ Centralized secrets management with access control.✅ Protects sensitive data with encryption.✅ Provides dynamic secrets, reducing exposure risk.
      
      These security tools work together to create a robust DevSecOps pipeline, ensuring security at every stage of development. 🚀💡


### Installation
1. Clone the repository:
   ```sh![download](https://github.com/user-attachments/assets/e81651ca-dc07-43b6-add0-174718a46da6)

   git clone https://github.com/0xfarben/ortho-secure.git
   cd ortho-secure
   ```
2. Set up environment variables and sonar properties [NOTE: Place this in root directory]:
   ```sh

   [Make sure you create a .env file and add up your values in .env]
   MYSQL_HOST=name_of_the_mysql_service_in_compose_file(mysql_db)
   MYSQL_DATABASE=dbortho
   MYSQL_USER=<your username> # admin
   MYSQL_PASSWORD=<Mysql password>
   MYSQL_ROOT_PASSWORD=<Root password>
   FLASK_ENV=development
   MYSQL_PORT=3306
   MYSQL_INITDB_SKIP_TZINFO=1
   SONAR_HOST_URL= "http://localhost:9000" or maybe different in your case [make sure it is reachable]
   SONAR_LOGIN= <your sonarqube login token>
   SECRET_KEY = <secret used in main.py for this project>
   MAIL_PASSWORD = <it's a mail password>


   [Make sure you create a sonar-project.properties file and add up your values in sonar-project.properties]
   sonar.projectKey=your_project_key_here
   sonar.token=your_sonar_token_here
   sonar.sources=.
   sonar.qualitygate.wait=true
   sonar.host.url=http://your_sonar_host_url_here
   sonar.python.version=your_python_version_here

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
   make sure your Sonar Scanner config properties are like this -- >
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


## ⭐ Support the Project  

If you found this helpful, consider **starring** ⭐ the repository and sharing it with your network! 🚀  

## License
This project is licensed under the terms specified in the `LICENSE` file.
