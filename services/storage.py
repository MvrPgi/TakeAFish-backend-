import os
import json
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from services.config import REFERENCE_COINS_DIAMETER_CM as coin_mapping
import logging


load_dotenv()


creds_json = os.getenv("GOOGLE_CREDS_JSON")
if not creds_json:
    raise Exception("Environment variable GOOGLE_CREDS_JSON not set!")

creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Fish Predictions").sheet1


def save_to_sheets(processed_result):
    """Append each detected fish to Google Sheets, right after header row."""
    try:
        current_values = sheet.get_all_values()
        start_row = len(current_values) + 1  


        coin_used = processed_result.get("coin_used", {"pixels_per_cm": None, "coin_label": None}) # Default if missing

        
        coin_label_raw = coin_used.get("coin_label")
        pixels_per_cm = coin_used.get("pixels_per_cm")

        if coin_label_raw is None:
            coin_label = "Default"
        else:
            coin_label = coin_mapping.get(coin_label_raw, "Unknown")

        for fish in processed_result["fish_detected"]:
            row = [
                fish.get("id"),
                fish.get("species"),
                fish.get("confidence"),
                fish.get("width_px"),
                fish.get("height_px"),
                fish.get("width_cm"),
                fish.get("height_cm"),
                fish.get("length_cm"),
                fish.get("area_cm2"),
                fish.get("days_before_maturity"),
                pixels_per_cm,
                coin_label,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ]
            sheet.insert_row(row, start_row)
            start_row += 1  

        logging.info("Successfully saved results to Google Sheets (after header).")

    except Exception as e:
        logging.error(f"Failed to save to Google Sheets: {e}")