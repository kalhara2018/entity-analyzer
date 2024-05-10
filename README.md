# entity-analyzer
Analyze , Compare and Sort entities from different sources


# Preparing Your Data Files
* Inside the files folder, create text files for each competitor.
* Name these files sequentially starting from comp1.txt, comp2.txt, and so forth. For example, if you have six competitors, your files should be named comp1.txt, comp2.txt, ..., comp6.txt.
* Ensure each file contains the relevant data for its respective competitor. This data is what will be analyzed by the TextRazor API.

## Setting Up TextRazor API

### Sign Up and API Key:
- Visit the [TextRazor Console](https://www.textrazor.com/console/) and sign up for an account.
- Opt for the Free plan, which includes 500 daily API requests.
- Obtain your API key, which is needed to make requests to TextRazor.

## Setting Up Google Sheets API

### Create a Google Cloud Project:
- Go to the [Google Cloud Project Creation Page](https://console.cloud.google.com/projectcreate) and start a new project.

### Enable Google Sheets API:
- Navigate to the "APIs & Services" dashboard within your Google Cloud console.
- Search for and enable the Google Sheets API.

### Configure OAuth Consent Screen:
- Set up the OAuth consent screen from the APIs & Services menu.

### Create a Service Account and Download Credentials:
- Under "Credentials," choose to create a new service account.
- Follow the prompts to name and assign the account.
- Generate a new key (choose JSON format) and download it.
- Rename this file to `credentials.json` and replace any existing file in your project directory.

### Prepare Your Google Sheet:
- Create a new Google Sheet in your Google Drive.
- Note the Sheet ID from the URL (it’s the string between `/d/` and `/edit` in the sheet URL).
- Share this Google Sheet with the client email found in your `credentials.json` file (usually something like `your-service-account@your-project.iam.gserviceauth.com`).

## Update API Key and Google Sheet ID in Your Code

Before running the script, make sure to replace placeholders with your actual credentials to ensure the script functions correctly.

### Replace TextRazor API Key:
- Locate the line in your code: `textrazor.api_key = "YOUR_TEXTRAZOR_API_HERE"`
- Replace `"YOUR_TEXTRAZOR_API_HERE"` with the API key you obtained from TextRazor.

### Replace Google Sheet ID:
- Locate the line in your code: `spreadsheet_id = "YOUR_GOOGLE_SHEET_ID"`
- Replace `"YOUR_GOOGLE_SHEET_ID"` with the Sheet ID you noted from your Google Sheet's URL.

### DONE
