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

- **service/dailyreport.py**
  - Generates and sends daily reports of fish species identifications.
  - Summarizes data and sends email notifications to stakeholders.

---

## API Endpoints
- **POST /upload**
  - Accepts an image file and coin reference.
  - Returns species identification and growth parameters.

  Example Request:
  ```bash
   ```bash
   curl -X POST http://localhost:8000/upload \
      -F "image=@path_to_image.jpg" \

   ```   

   Example Response:
   ```json
   
     "coin_used": {
       "coin_confidence": 0.8674470782279968,
       "coin_diameter_cm": 2.3,
       "coin_label": "1_PESO",
       "message": "Coin calibration successful",
       "pixels_per_cm": 37.39130434782609,
       "width_px": 86.0
     },
     "fish_detected": 
       {
       "area_cm2": 61.198347755543516,
       "confidence": 0.5997757911682129,
       "days_before_maturity": 418.05,
       "height_cm": 12.783720930232557,
       "height_px": 478.0,
       "id": "4ee76963-c099-48d2-b240-8932f6966d73",
       "length_cm": 12.783720930232557,
       "species": "Tulingan",
       "width_cm": 4.78720930232558,
       "width_px": 179.0
       }

   ```




## Setup Instructions For Google Sheets Integration

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

## Set Up Instructions For Email Notifications

1. **Create a Gmail Account**
   - Create a new Gmail account to send emails from (e.g., `fishreports@gmail.com`).

2. **Enable "Less Secure App Access"**

    - Go to app passwords.google.com.
    - Select "Other (Custom name)" and enter a name (e.g., `TakeAFishApp`).
    - Click Generate and copy the 16-character app password.

3. **Update Email Configuration in `dailyreport.py`**
    - Open `services/dailyreport.py`.
    - Update the `GMAIL_ADDRESS` and `EMAIL_PASSWORD` variables with your Gmail address and the generated app password.
    ```python
    GMAIL_ADDRESS = "fishreports@gmail.com"

    GMAIL_APP_PASSWORD = "your_generated_app_password"

    REPORT_RECIPIENTS = ["recipient1@example.com", "recipient2@example.com"]
    ```


