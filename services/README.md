# Services

This directory contains the core services for the TakeAFish backend application. Each service is responsible for a specific functionality, such as image processing, species identification, and data storage.

## Service Modules

- **services/utils.py**
  - Utility functions for image processing and model inference.
  - Handles loading images, preprocessing for model input, and post-processing outputs.

- **services/species.py**
  - Responsible for species identification and growth parameter calculations.
  - Uses machine learning models to classify fish species and estimate growth from image data.
- **services/monthlyforecast.py**
  - Generates monthly growth forecasts for identified fish species.
  - Utilizes growth models and parameters to predict fish size over time.
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
### POST /upload
**Description:** Upload an image for fish species identification and age estimation

  Example Request:
  ```bash
   ```bash
   curl -X POST http://localhost:8000/upload \
      -F "image=@path_to_image.jpg" \

   ```   

   Example Response:
   ```json success response 200
   
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
   ``` json error response 400
  {"error": "No image file provided"}  
  {"error": "File size exceeds 3MB limit"} 
  {"error": "Unsupported file type"}  
  {"error": "No fish detected in image"}  
  {"error": "Internal server error"} 
   ```
### POST /monthly-forecast
**Description:** Generate a monthly growth forecast for a given fish species and current size
- Example Request:
  ```bash
   curl -X POST http://localhost:8000/monthly-forecast \
      -H "Content-Type: application/json" \
      -d '{"TILAPIA":365  "ISLAND MACKEREL": 100,"LAPU-LAPU": 300,"TULINGAN": 400,"BANGUS": 500}'
   ```


  #### Example Response

  ```json
  {
    "forecasts": {
      "TILAPIA": {
        "current_status": {
          "current_age_years": 3.47,
          "current_length_cm": 32.72,
          "days_before_maturity": 222,
          "maturity_age_years": 4.08,
          "maturity_length_cm": 35.36
        },
        "monthly_forecast": [
          {
            "month": 1,
            "date": "2025-12-11",
            "age_years": 3.55,
            "growth_cm": 0.4,
            "length_cm": 33.12,
            "total_growth_cm": 0.4
          }
          // ... 11 more months
        ]
      },
      "BANGUS": {
        "current_status": {
          "current_age_years": 17.27,
          "current_length_cm": 23.19,
          "days_before_maturity": 222,
          "maturity_age_years": 17.88,
          "maturity_length_cm": 23.52
        },
        "monthly_forecast": [
          // ... monthly forecast data
        ]
      }
    },
    "generated_date": "2025-11-11T22:56:10.447800",
    "message": "Monthly forecast generated successfully"
  }
  ```

  #### Error Responses

  ```json
  {"error": "Invalid species provided"}
  {"error": "Internal server error"}



### GET /monthly-forecast-page

**Description:** Displays a web page with a form to generate monthly growth forecasts for fish species.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/monthly-forecast-page?species=TILAPIA&current_size_cm=30&current_age_days=365"
```

**Page Features:**
- Interactive form to input multiple species and their details.
- Fields for species name and days before maturity.
- Option to add more species dynamically.
- Button to submit and generate forecast.
- Displays forecast results in JSON format.

**Example HTML Response:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monthly Growth Forecast</title>
</head>
<body>
  <div class="container">
    <h2>Monthly Growth Forecast</h2>
    <div id="inputList">
      <div class="input-group">
        <input type="text" placeholder="Species (e.g., TILAPIA)" class="species-input">
        <input type="number" placeholder="Days before maturity" class="days-input">
      </div>
    </div>
    <button class="add-btn" onclick="addSpeciesInput()">+ Add Species</button><br><br>
    <button onclick="submitForecast()">Generate Forecast</button>
    <pre id="jsonOutput" class="json-output"></pre>
  </div>
</body>
</html>
```

### GET /health
**Description:** Health check endpoint to verify the service is running
- Example Request:
  ```bash
   curl -X GET http://localhost:8000/health
   ```
   Example Response:
   ```json success response 200
   {
     "status": "healthy", 
     "service": "takeafish-backend",
     "timestamp": "2023-10-01T12:00:00"
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

## Set Up Daily Report Scheduling
- Use a task scheduler like `cron` (Linux/Mac) or Task Scheduler (Windows) to run `dailyreport.py` at a specific time each day.
- Example `cron` entry to run at 8 AM daily:
  ```cron
  0 8 * * * /path/to/your/python /path/to/services/dailyreport.py
  ```
- Ensure the script has execute permissions: `chmod +x dailyreport.py`.
- Test the scheduling by running the script manually first to ensure it works as expected.
- Check your email for the report to confirm successful execution.
- In My case, I used Github Actions to schedule the daily report. You can set up a workflow in your GitHub repository to run the `dailyreport.py` script at a specified time each day using GitHub Actions' scheduling feature. 

refer to the [GitHub Actions documentation](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#scheduled-events) for more details on how to set this up.