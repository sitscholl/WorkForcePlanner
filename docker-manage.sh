#!/bin/bash

# Workforce Planner Docker Management Script

set -e

CONTAINER_NAME="workforce-planner-app"
IMAGE_NAME="workforce-planner"

case "$1" in
    "build")
        echo "Building Docker image..."
        docker build -t $IMAGE_NAME .
        echo "✅ Docker image built successfully!"
        ;;
    "start")
        echo "Starting Workforce Planner..."
        docker-compose up -d
        echo "✅ Workforce Planner is running!"
        echo "🌐 Access the app at: http://localhost:8501"
        ;;
    "stop")
        echo "Stopping Workforce Planner..."
        docker-compose down
        echo "✅ Workforce Planner stopped!"
        ;;
    "restart")
        echo "Restarting Workforce Planner..."
        docker-compose down
        docker-compose up -d
        echo "✅ Workforce Planner restarted!"
        echo "🌐 Access the app at: http://localhost:8501"
        ;;
    "logs")
        echo "Showing logs..."
        docker-compose logs -f
        ;;
    "shell")
        echo "Opening shell in container..."
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;
    "clean")
        echo "Cleaning up Docker resources..."
        docker-compose down
        docker rmi $IMAGE_NAME 2>/dev/null || true
        echo "✅ Cleanup complete!"
        ;;
    *)
        echo "Workforce Planner Docker Management"
        echo ""
        echo "Usage: $0 {build|start|stop|restart|logs|shell|clean}"
        echo ""
        echo "Commands:"
        echo "  build   - Build the Docker image"
        echo "  start   - Start the application"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  logs    - Show application logs"
        echo "  shell   - Open shell in container"
        echo "  clean   - Remove container and image"
        echo ""
        echo "Quick start:"
        echo "  1. $0 build"
        echo "  2. $0 start"
        echo "  3. Open http://localhost:8501 in your browser"
        exit 1
        ;;
esac