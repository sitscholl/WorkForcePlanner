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
5. Download the JSON file and save it securely

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