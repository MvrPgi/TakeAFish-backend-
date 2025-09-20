import os
import smtplib
import gspread
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from oauth2client.service_account import ServiceAccountCredentials
import logging


# Load .env file
load_dotenv()

EMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
REPORT_RECIPIENT = os.getenv("REPORT_RECIPIENT")

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("Missing Gmail credentials in .env")

if not GOOGLE_CREDS_JSON:
    raise ValueError("Missing Google credentials JSON in .env")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Fish Predictions").sheet1  # Open the Google Sheet
data = sheet.get_all_records()  # Get all data from the sheet


one_day_ago = datetime.now() - timedelta(days=1)
recent_data = [row for row in data if datetime.strptime(row["Date/Time"], "%Y-%m-%d %H:%M:%S") >= one_day_ago]

total_fish = len(recent_data)
species_count = {}
for row in recent_data:
    species = row["Species"]
    species_count[species] = species_count.get(species, 0) + 1

species_rows = "".join(
    f"<tr><td>{species}</td><td style='text-align:right;'>{count}</td></tr>"
    for species, count in species_count.items()
) or "<tr><td colspan='2' style='text-align:center;color:#777;'>No data recorded this day</td></tr>"


with open("templates/email_template.html", "r", encoding="utf-8") as f:
    html_template = f.read()

html_content = html_template.replace("{{total_fish}}", str(total_fish)) \
                           .replace("{{species_rows}}", species_rows) \
                           .replace("{{generated_at}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def send_report():
    try:
        recipient = REPORT_RECIPIENT

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = "Daily Fish Detection Report"
        msg.attach(MIMEText(html_content, "html"))

        # --- Option 1: SSL (recommended) ---
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())

        logging.info("Daily report email sent successfully via SSL!")

    except smtplib.SMTPNotSupportedError:
        # --- Option 2: Fallback to STARTTLS if SSL fails ---
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
            print("Daily report email sent successfully via STARTTLS!")

    except Exception as e:
        import logging
        logging.error(f" Failed to send daily report email: {e}")
send_report()