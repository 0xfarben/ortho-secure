#!/bin/bash

# Create the Trivy reports directory
# mkdir -p trivy_reports/kubernetes

# Debugging: List files in the services directory
echo "Listing files in kubernetes/services:"
ls -l kubernetes/services

# Scan configmaps
trivy config kubernetes/configmaps -f table -o trivy_reports/kubernetes/configmaps_report.txt

# Scan deployments
trivy config kubernetes/deployments -f table -o trivy_reports/kubernetes/deployments_report.txt

# Scan policies
trivy config kubernetes/policies -f table -o trivy_reports/kubernetes/policies_report.txt


# Debugging: List files in the services directory
echo "Listing files in kubernetes/services before scan:"
ls -l kubernetes/services

echo "Trivy scans completed and reports saved in trivy_reports/kubernetes"
