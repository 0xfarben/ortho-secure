# mkdir -p trivy_reports  # Create a directory for reports

# Get images of running containers and scan them
for container in $(docker ps --format "{{.ID}}"); do
    image_name=$(docker inspect --format='{{.Config.Image}}' $container)
    echo "Scanning image: $image_name (Running in container: $container)..."
    
    # Run Trivy scan and save report
    trivy image --severity HIGH,CRITICAL --ignore-unfixed $image_name > trivy_reports/"$(echo $image_name | tr '/' '_').txt"
done

echo "Scan reports for running container images saved in 'trivy_reports/' directory."
