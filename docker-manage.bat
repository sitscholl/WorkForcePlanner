@echo off
setlocal

set CONTAINER_NAME=workforce-planner-app
set IMAGE_NAME=workforce-planner

if "%1"=="build" (
    echo Building Docker image...
    docker build -t %IMAGE_NAME% .
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Docker image built successfully!
    ) else (
        echo ❌ Failed to build Docker image
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
echo Usage: %0 {build^|start^|stop^|restart^|logs^|shell^|clean}
echo.
echo Commands:
echo   build   - Build the Docker image
echo   start   - Start the application
echo   stop    - Stop the application
echo   restart - Restart the application
echo   logs    - Show application logs
echo   shell   - Open shell in container
echo   clean   - Remove container and image
echo.
echo Quick start:
echo   1. %0 build
echo   2. %0 start
echo   3. Open http://localhost:8501 in your browser