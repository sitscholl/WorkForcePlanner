@echo off
setlocal

set CONTAINER_NAME=workforce-planner-app
set IMAGE_NAME=ghcr.io/sitscholl/workforce-planner-app:latest

if "%1"=="pull" (
    echo Pulling latest image from GitHub Container Registry...
    docker pull %IMAGE_NAME%
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Latest image pulled successfully!
    ) else (
        echo ❌ Failed to pull latest image
        exit /b 1
    )
    goto :eof
)

if "%1"=="start" (
    echo Starting Workforce Planner...
    docker-compose up -d
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Workforce Planner is running!
        echo 🌐 Access the app at: http://localhost:8501
    ) else (
        echo ❌ Failed to start Workforce Planner
        exit /b 1
    )
    goto :eof
)

if "%1"=="stop" (
    echo Stopping Workforce Planner...
    docker-compose down
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Workforce Planner stopped!
    ) else (
        echo ❌ Failed to stop Workforce Planner
        exit /b 1
    )
    goto :eof
)

if "%1"=="restart" (
    echo Restarting Workforce Planner...
    docker-compose down
    docker-compose up -d
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Workforce Planner restarted!
        echo 🌐 Access the app at: http://localhost:8501
    ) else (
        echo ❌ Failed to restart Workforce Planner
        exit /b 1
    )
    goto :eof
)

if "%1"=="logs" (
    echo Showing logs...
    docker-compose logs -f
    goto :eof
)

if "%1"=="shell" (
    echo Opening shell in container...
    docker exec -it %CONTAINER_NAME% /bin/bash
    goto :eof
)

if "%1"=="clean" (
    echo Cleaning up Docker resources...
    docker-compose down
    docker rmi %IMAGE_NAME% 2>nul
    echo ✅ Cleanup complete!
    goto :eof
)

echo Workforce Planner Docker Management
echo.
echo Usage: %0 {pull^|start^|stop^|restart^|logs^|shell^|clean}
echo.
echo Commands:
echo   pull    - Pull latest image from GitHub Container Registry
echo   start   - Start the application
echo   stop    - Stop the application
echo   restart - Restart the application
echo   logs    - Show application logs
echo   shell   - Open shell in container
echo   clean   - Remove container and image
echo.
echo Quick start:
echo   1. %0 pull
echo   2. %0 start
echo   3. Open http://localhost:8501 in your browser