import base64
import os
import smtplib
import gspread
import json
import csv
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
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
if not GOOGLE_CREDS_JSON:
    raise ValueError("Missing Google credentials JSON in environment")

try:
    creds_dict = json.loads(base64.b64decode(GOOGLE_CREDS_JSON))
except Exception:
    creds_dict = json.loads(GOOGLE_CREDS_JSON)


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Fish Predictions").sheet1


def get_recent_data():
    """Fetch fish predictions from the last 24 hours."""
    try:
        data = sheet.get_all_records()
    except Exception as e:
        logging.error(f"Failed to fetch Google Sheet data: {e}")
        return []

    one_day_ago = datetime.now() - timedelta(days=7)
    recent_data = []
    for row in data:
        try:
            dt = datetime.strptime(row["Date/Time"], "%Y-%m-%d %H:%M:%S")
            if dt >= one_day_ago:
                recent_data.append(row)
        except (ValueError, KeyError):
            logging.warning(f"Skipping row due to missing or invalid Date/Time: {row}")
    return recent_data


def build_csv_file(recent_data):
    """Generate a daily CSV report and return the filename."""
    folder = "reports"  
    os.makedirs(folder, exist_ok=True)  

    filename = os.path.join(folder, f"daily_report_{datetime.now().strftime('%Y%m%d')}.csv")
    headers = ["INTERFERENCE ID", "Species", "Confidence", "Width (px)", "Height (px)", 
               "Width (cm)", "Height (cm)", "Length (cm)", "Area (cm²)", 
               "Days Before Maturity", "Pixels per cm", "Coin Label", "Coin Confidence", "Date/Time"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in recent_data:
            writer.writerow({
                "INTERFERENCE ID": row.get("INTERFERENCE ID", ""),
                "Species": row.get("Species", ""),
                "Confidence": row.get("Confidence", ""),
                "Width (px)": row.get("Width (px)", ""),
                "Height (px)": row.get("Height (px)", ""),
                "Width (cm)": row.get("Width (cm)", ""),
                "Height (cm)": row.get("Height (cm)", ""),
                "Length (cm)": row.get("Length (cm)", ""),
                "Area (cm²)": row.get("Area (cm²)", ""),
                "Days Before Maturity": row.get("Days Before Maturity", ""),
                "Pixels per cm": row.get("Pixels per cm", ""),
                "Coin Label": row.get("Coin Label", ""),
                "Coin Confidence": row.get("Coin Confidence", ""),
                "Date/Time": row.get("Date/Time", "")
            })

    return filename


def build_email_content(recent_data):
    total_fish = len(recent_data)
    species_count = {}
    for row in recent_data:
        species = row.get("Species", "Unknown")
        species_count[species] = species_count.get(species, 0) + 1

    species_rows = "".join(
        f"<tr><td>{species}</td><td style='text-align:right;'>{count}</td></tr>"
        for species, count in species_count.items()
    ) or "<tr><td colspan='2' style='text-align:center;color:#777;'>No data recorded this day</td></tr>"

    with open("templates/email_template.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    return html_template.replace("{{total_fish}}", str(total_fish)) \
                        .replace("{{species_rows}}", species_rows) \
                        .replace("{{generated_at}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def send_report():
    """Send daily fish detection report via email and delete CSV after use."""
    recent_data = get_recent_data()
    if not recent_data:
        logging.info("No recent data to report.")
        return

    csv_file = build_csv_file(recent_data)
    html_content = build_email_content(recent_data)

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = REPORT_RECIPIENT
        msg["Subject"] = "Daily Fish Detection Report"
        msg.attach(MIMEText(html_content, "html"))

        # Attach CSV file
        with open(csv_file, "rb") as f:
            from email.mime.application import MIMEApplication
            part = MIMEApplication(f.read(), Name=os.path.basename(csv_file))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(csv_file)}"'
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, REPORT_RECIPIENT, msg.as_string())

        logging.info("Daily report email sent successfully via SSL!")
    except smtplib.SMTPNotSupportedError:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, REPORT_RECIPIENT, msg.as_string())
        logging.info("Daily report email sent successfully via STARTTLS!")
    except Exception as e:
        logging.error(f"Failed to send daily report email: {e}")

    # Delete local file
    os.remove(csv_file)
    logging.info(f"Deleted local file {csv_file}")

    # Clear the sheet and reset headers
    sheet.clear()
    sheet.append_row(["INTERFERENCE ID", "Species", "Confidence", "Width (px)", "Height (px)", "Width (cm)", "Height (cm)", "Length (cm)", "Area (cm²)", "Days Before Maturity", "Pixels per cm", "Coin Label", "Coin Confidence", "Date/Time"])
    logging.info("Google Sheet cleared and headers restored.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    send_report()
