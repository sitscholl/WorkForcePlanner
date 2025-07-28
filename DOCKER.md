# Docker Setup for Workforce Planner

This document explains how to run the Workforce Planner Streamlit application using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Pushing to Github Container Registry

The script `docker-publish.bat` automates the process of building, tagging, and pushing the Docker image to the GitHub Container Registry. To run it, you need a PersonalAccess Token with write:packages, read:packages, and delete:packages scopes. Create one here: https://github.com/settings/tokens

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and start the application:**
   ```bash
   # On Linux/Mac
   ./docker-manage.sh build
   ./docker-manage.sh start
   
   # On Windows
   docker-manage.bat build
   docker-manage.bat start
   ```

2. **Access the application:**
   Open your browser and go to: http://localhost:8501

### Option 2: Manual Docker Commands

1. **Build the Docker image:**
   ```bash
   docker build -t workforce-planner .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name workforce-planner-app \
     -p 8501:8501 \
     -v $(pwd)/config:/app/config \
     -v $(pwd)/gsheets_creds.json:/app/gsheets_creds.json:ro \
     workforce-planner
   ```

## Configuration Persistence

The Docker setup ensures that your configuration files in the `config/` directory are persisted between container restarts. This is achieved through volume mounting:

- `./config:/app/config` - Mounts your local config directory to the container
- `./gsheets_creds.json:/app/gsheets_creds.json:ro` - Mounts Google Sheets credentials (read-only)

## Management Commands

### Using the Management Scripts

**Linux/Mac (`docker-manage.sh`):**
```bash
./docker-manage.sh build    # Build the Docker image
./docker-manage.sh start    # Start the application
./docker-manage.sh stop     # Stop the application
./docker-manage.sh restart  # Restart the application
./docker-manage.sh logs     # View application logs
./docker-manage.sh shell    # Open shell in container
./docker-manage.sh clean    # Remove container and image
```

**Windows (`docker-manage.bat`):**
```cmd
docker-manage.bat build    # Build the Docker image
docker-manage.bat start    # Start the application
docker-manage.bat stop     # Stop the application
docker-manage.bat restart  # Restart the application
docker-manage.bat logs     # View application logs
docker-manage.bat shell    # Open shell in container
docker-manage.bat clean    # Remove container and image
```

### Using Docker Compose Directly

```bash
docker-compose up -d        # Start in background
docker-compose down         # Stop and remove containers
docker-compose logs -f      # Follow logs
docker-compose restart      # Restart services
```

## Troubleshooting

### Port Already in Use
If port 8501 is already in use, you can change it in `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Change 8502 to any available port
```

### Configuration Issues
1. Ensure your `config/` directory exists and contains the necessary YAML files
2. Check that `config/gsheets_creds.json` exists if using Google Sheets integration
3. Verify file permissions allow Docker to read the mounted files

### Container Health
Check if the container is healthy:
```bash
docker ps                           # Check container status
docker logs workforce-planner-app   # View container logs
```

### Rebuilding After Code Changes
When you make changes to the application code:
```bash
# Linux/Mac
./docker-manage.sh clean
./docker-manage.sh build
./docker-manage.sh start

# Windows
docker-manage.bat clean
docker-manage.bat build
docker-manage.bat start
```

## Docker Files Overview

- `Dockerfile` - Defines the container image
- `docker-compose.yml` - Orchestrates the container with proper volume mounts
- `.dockerignore` - Excludes unnecessary files from the build context
- `requirements.txt` - Python dependencies extracted from pyproject.toml
- `docker-manage.sh` / `docker-manage.bat` - Management scripts for easy operation

## Security Notes

- The Google Sheets credentials file is mounted as read-only
- The container runs as a non-root user where possible
- Only necessary ports are exposed
- Configuration files are persisted locally, not in the container

## Performance Tips

- The container includes health checks to ensure the app is running properly
- File watching is disabled in the container for better performance
- Python bytecode caching is optimized for container environments