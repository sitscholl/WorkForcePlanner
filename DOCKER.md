# Docker Setup for Workforce Planner

This document explains how to run the Workforce Planner Streamlit application using Docker with pre-built images from GitHub Container Registry.

## Quick Workflow

For end users:

1. docker-manage.bat pull (or .sh pull on Linux/Mac)
2. docker-manage.bat start
3. Access at http://localhost:8501

For developers:

1. Make code changes
2. Run docker-publish.bat to build and publish new image
3. End users run docker-manage.bat pull to get updates

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Image Distribution

The application is distributed as a pre-built Docker image via GitHub Container Registry (GHCR). This eliminates the need to build the image locally and ensures consistent deployments.

### Publishing New Versions (For Developers)

The script `docker-publish.bat` automates the process of building, tagging, and pushing the Docker image to the GitHub Container Registry. To run it, you need a Personal Access Token with `write:packages`, `read:packages`, and `delete:packages` scopes. Create one here: https://github.com/settings/tokens

## Quick Start

### Option 1: Using Docker Management Scripts (Recommended)

1. **Pull the latest image and start the application:**
   ```bash
   # On Linux/Mac
   ./docker-manage.sh pull
   ./docker-manage.sh start
   
   # On Windows
   docker-manage.bat pull
   docker-manage.bat start
   ```

2. **Access the application:**
   Open your browser and go to: http://localhost:8501

### Option 2: Using Docker Compose Directly

1. **Pull the latest image:**
   ```bash
   docker pull ghcr.io/sitscholl/workforce-planner-app:latest
   ```

2. **Start the application:**
   ```bash
   docker-compose up -d
   ```

### Option 3: Manual Docker Commands

1. **Pull the image:**
   ```bash
   docker pull ghcr.io/sitscholl/workforce-planner-app:latest
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name workforce-planner-app \
     -p 8501:8501 \
     -v $(pwd)/config:/app/config \
     ghcr.io/sitscholl/workforce-planner-app:latest
   ```

## Configuration Persistence

The Docker setup ensures that your configuration files in the `config/` directory are persisted between container restarts. This is achieved through volume mounting:

- `./config:/app/config` - Mounts your local config directory to the container

## Management Commands

### Using the Management Scripts

**Linux/Mac (`docker-manage.sh`):**
```bash
./docker-manage.sh pull     # Pull latest image from GitHub Container Registry
./docker-manage.sh start    # Start the application
./docker-manage.sh stop     # Stop the application
./docker-manage.sh restart  # Restart the application
./docker-manage.sh logs     # View application logs
./docker-manage.sh shell    # Open shell in container
./docker-manage.sh clean    # Remove container and image
```

**Windows (`docker-manage.bat`):**
```cmd
docker-manage.bat pull     # Pull latest image from GitHub Container Registry
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

## Updating the Application

To update to the latest version of the application:

1. **Using management scripts:**
   ```bash
   # Linux/Mac
   ./docker-manage.sh stop
   ./docker-manage.sh pull
   ./docker-manage.sh start
   
   # Windows
   docker-manage.bat stop
   docker-manage.bat pull
   docker-manage.bat start
   ```

2. **Using Docker Compose:**
   ```bash
   docker-compose down
   docker pull ghcr.io/sitscholl/workforce-planner-app:latest
   docker-compose up -d
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

### Image Pull Issues
If you encounter issues pulling the image:
```bash
# Check if you can access the registry
docker pull ghcr.io/sitscholl/workforce-planner-app:latest

# If authentication is required, login first
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

## Docker Files Overview

- `Dockerfile` - Defines the container image (used for building and publishing)
- `docker-compose.yml` - Orchestrates the container with proper volume mounts
- `docker-publish.bat` - Script to build and publish images to GitHub Container Registry
- `docker-manage.sh` / `docker-manage.bat` - Management scripts for easy operation

## Security Notes

- The container runs as a non-root user where possible
- Only necessary ports are exposed
- Configuration files are persisted locally, not in the container
- Images are distributed through GitHub Container Registry with proper access controls

## Performance Tips

- The container includes health checks to ensure the app is running properly
- File watching is disabled in the container for better performance
- Python bytecode caching is optimized for container environments
- Pre-built images eliminate build time and ensure consistent deployments