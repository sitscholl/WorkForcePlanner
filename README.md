# Workforce Planner

A Streamlit-based application for planning and scheduling agricultural workforce, specifically designed for apple field labor management. The application helps optimize worker allocation across different fields and harvest periods.

## Features

- **Field Management**: Configure and manage multiple fields with different characteristics
- **Workforce Planning**: Allocate workers efficiently across fields and time periods
- **Variety-Based Scheduling**: Support for different start dates based on apple variety groups (early, main, late)
- **Google Sheets Integration**: Import field data directly from Google Sheets
- **Interactive Dashboard**: Web-based interface for easy planning and visualization
- **Docker Support**: Easy deployment using pre-built Docker images

## Quick Start with Docker (Recommended)

The easiest way to run the Workforce Planner is using Docker with our pre-built images from GitHub Container Registry.

### Prerequisites
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

### Installation & Setup

1. **Clone or download this repository**
2. **Pull the latest image and start the application:**
   ```bash
   # On Linux/Mac
   ./docker-manage.sh pull
   ./docker-manage.sh start
   
   # On Windows
   docker-manage.bat pull
   docker-manage.bat start
   ```
3. **Access the application:**
   Open your browser and go to: http://localhost:8501

### Docker Management Commands

**Linux/Mac:**
```bash
./docker-manage.sh pull     # Pull latest version
./docker-manage.sh start    # Start the application
./docker-manage.sh stop     # Stop the application
./docker-manage.sh restart  # Restart the application
./docker-manage.sh logs     # View application logs
./docker-manage.sh clean    # Remove container and image
```

**Windows:**
```cmd
docker-manage.bat pull     # Pull latest version
docker-manage.bat start    # Start the application
docker-manage.bat stop     # Stop the application
docker-manage.bat restart  # Restart the application
docker-manage.bat logs     # View application logs
docker-manage.bat clean    # Remove container and image
```

For detailed Docker setup information, see [DOCKER.md](DOCKER.md).

## Manual Installation (Alternative)

If you prefer to run the application without Docker:

1. **Install Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install streamlit pandas pyyaml gspread oauth2client
   ```
3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Configuration

The application uses YAML configuration files stored in the `config/` directory:

- `config.yaml` - Main application configuration
- `field_collection_YYYY.yaml` - Field data for specific years
- `Workforce_YYYY.yaml` - Workforce data for specific years

### Configuration Persistence

When using Docker, your configuration files are automatically persisted between container restarts through volume mounting.

## Google Sheets Integration Setup

To use Google Sheets integration, you need to set up Google Cloud credentials:

### Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API

### Step 2: Create Service Account Credentials
1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Fill in the service account details:
   - Name: `apple-field-planner`
   - Description: `Service account for Apple Field Labor Planning`
4. Click "Create and Continue"
5. Skip the optional role assignment (click "Continue")
6. Click "Done"

### Step 3: Generate JSON Key
1. Click on your newly created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format and click "Create"
5. Download the JSON file and save it as `config/gsheets_creds.json`

### Step 4: Share Your Spreadsheet
1. Open your Google Spreadsheet containing field data
2. Click the "Share" button
3. Add the service account email (found in the JSON file) as an editor
4. Make sure "Notify people" is unchecked
5. Click "Share"

## Scheduling Configuration

The workforce planner supports different start dates for different variety groups. This allows you to schedule work for early varieties, main varieties, and late varieties at different times.

### Configuration Format

In your `config.yaml` file, you can specify different start dates for each variety group:

```yaml
start_date:
  frühsorte: '2025-08-24'    # Early varieties start date
  hauptsorte: '2025-09-17'   # Main varieties start date
  spätsorte: '2025-10-17'    # Late varieties start date
```

### Field Data Requirements

Your field data must include a column that specifies the variety group for each field. By default, this column should be named "Variety Group", but you can customize this in the scheduler function.

Example field data structure:
```
Field Name          | Variety Group | Hours Required | Harvest Round
Parleng (Gala)      | frühsorte    | 120           | 1
Gasslwiese (Golden) | hauptsorte   | 80            | 1
Neuacker (Golden)   | spätsorte    | 95            | 1
```

### How It Works

1. Fields are grouped by their variety group
2. Each group is scheduled starting from its specified start date
3. Work is scheduled sequentially within each group
4. The scheduler ensures no overlapping work between groups
5. Later groups will start either at their specified date or after the previous group finishes, whichever is later

## Application Structure

- `app.py` - Main Streamlit application
- `pages/` - Additional application pages
  - `2_Workforce.py` - Workforce management
  - `3_Fields.py` - Field management
  - `4_Model.py` - Planning models
  - `5_Settings.py` - Application settings
- `config/` - Configuration files and credentials
- `docker-compose.yml` - Docker orchestration
- `docker-manage.*` - Docker management scripts

## Updating the Application

To update to the latest version:

```bash
# Using Docker (recommended)
./docker-manage.sh stop
./docker-manage.sh pull
./docker-manage.sh start

# Or on Windows
docker-manage.bat stop
docker-manage.bat pull
docker-manage.bat start
```

## Development

For developers who want to contribute or build custom images:

1. **Make your changes to the code**
2. **Build and publish a new image:**
   ```cmd
   docker-publish.bat
   ```
3. **Users can then update with:**
   ```bash
   ./docker-manage.sh pull
   ```

## Support

- Check the [DOCKER.md](DOCKER.md) file for detailed Docker setup and troubleshooting
- Review configuration files in the `config/` directory for examples
- Ensure Google Sheets credentials are properly configured if using that integration

## License

This project is designed for agricultural workforce planning and management.