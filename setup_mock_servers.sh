#!/bin/bash
set -e

# Create directories and move files
for service in sso jira confluence opensearch springboot_admin grafana; do
    dir="mock_servers/mock_${service}_server"
    mkdir -p "$dir"
    
    # Move the python script into the subdirectory if it exists in mock_servers/
    if [ -f "mock_servers/${service}_server.py" ]; then
        mv "mock_servers/${service}_server.py" "$dir/main.py"
        
        # Add health check to the python script
        cat << 'HEALTH' >> "$dir/main.py"

@app.get("/health")
async def health():
    return {"status": "ok"}
HEALTH

    fi

    # Create Dockerfile
    # Parse port from docker-compose or hardcode based on service
    port="80"
    if [ "$service" == "sso" ]; then port="8090"; fi
    if [ "$service" == "jira" ]; then port="8081"; fi
    if [ "$service" == "confluence" ]; then port="8082"; fi
    if [ "$service" == "opensearch" ]; then port="9200"; fi
    if [ "$service" == "springboot_admin" ]; then port="9300"; fi
    if [ "$service" == "grafana" ]; then port="3001"; fi
    
    cat << DOCKER > "$dir/Dockerfile"
FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic python-multipart
COPY mock_servers/mock_${service}_server/main.py /app/main.py
EXPOSE $port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$port"]
DOCKER

done

# Create seed data
mkdir -p mock_servers/seed_data
echo "tickets: []" > mock_servers/seed_data/jira.yaml
echo "pages: []" > mock_servers/seed_data/confluence.yaml
echo "logs: []" > mock_servers/seed_data/opensearch.yaml

# Create health check script for 3.10
cat << 'HEALTH' > mock_servers/health_check.sh
#!/bin/bash
# Check all mock services
for port in 8090 8081 8082 9200 9300 3001; do
    if curl -s -f http://localhost:$port/health > /dev/null; then
        echo "Service on port $port is UP"
    else
        echo "Service on port $port is DOWN"
        exit 1
    fi
done
echo "All mock services are healthy."
HEALTH
chmod +x mock_servers/health_check.sh
chmod +x setup_mock_servers.sh
./setup_mock_servers.sh
