# Services

This directory contains the core services for the TakeAFish backend application. Each service is responsible for a specific functionality, such as image processing, species identification, and data storage.

## Service Modules

- **services/utils.py**
  - Utility functions for image processing and model inference.
  - Handles loading images, preprocessing for model input, and post-processing outputs.

- **services/species.py**
  - Responsible for species identification and growth parameter calculations.
  - Uses machine learning models to classify fish species and estimate growth from image data.

- **services/storage.py**
  - Manages data storage, including saving results to Google Sheets.
  - Handles Google API authentication and ensures correct data formatting.

- **services/config.py**
  - Contains configuration settings and constants used across services.
  - Includes model paths, class mappings, and other parameters.

---

## Setup Instructions

1. **Create the Google Sheet**
   - Go to Google Sheets and create a new blank sheet.
   - Rename it (e.g., `Fish Predictions`).
   - Add headers in the first row:  
    `INTERFERENCE ID | Species | Confidence | Width (px) | Height (px) | Width (cm) | Height (cm) | Length (cm) | Area (cm²) | Days Before Maturity | Pixels per cm | Coin Label | Date/Time`

2. **Create a Google Cloud Project & Enable API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project (e.g., `CapstoneFishApp`).
   - Navigate to APIs & Services → Library.
   - Search for "Google Sheets API" and enable it.

3. **Create a Service Account**
   - In Cloud Console, go to IAM & Admin → Service Accounts.
   - Create a new service account (e.g., `capstone-bot`).
   - Grant the Editor role (or at least Sheets Editor).
   - Go to the service account → Keys → Add Key → Create New Key → JSON.
   - Download the JSON key file (e.g., `service_account.json`).

4. **Share the Sheet With the Service Account**
   - Open your Google Sheet.
   - Click Share → Share with people and groups.
   - Paste the service account email from the JSON file.
   - Give it Editor access and click Send.

5. **Install Required Python Packages**
   - Install dependencies using pip:
     ```bash
     pip install gspread google-auth flask
     ```

6. **Test the Integration**
   - Run your Python code to send a test prediction.
   - If successful, a new row should appear in your Google Sheet.

7. **Integrate With Flask**
   - On successful prediction, call a function like `send_prediction_to_sheet(prediction_dict)`.
   - Each prediction will automatically append to the sheet in real time.
