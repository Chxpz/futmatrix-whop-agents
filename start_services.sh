#!/bin/bash

# Start Docker services script for AI Agents System
echo "Starting AI Agents System infrastructure..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed or not in PATH"
    exit 1
fi

# Start services
echo "Starting RabbitMQ and Redis services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose ps | grep -q "healthy"; then
        rabbitmq_healthy=$(docker-compose ps rabbitmq | grep -c "healthy")
        redis_healthy=$(docker-compose ps redis | grep -c "healthy")
        
        if [ "$rabbitmq_healthy" -eq 1 ] && [ "$redis_healthy" -eq 1 ]; then
            echo "All services are healthy!"
            break
        fi
    fi
    
    echo "Waiting for services... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -eq $timeout ]; then
    echo "Warning: Services may not be fully ready yet"
fi

# Show service status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "Services started successfully!"
echo "RabbitMQ Management UI: http://localhost:15672 (admin/admin123)"
echo "Redis: localhost:6379"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"