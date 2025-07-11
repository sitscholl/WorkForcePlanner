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