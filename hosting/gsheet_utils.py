import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "Agent click logs"  # Must match your Google Sheet name

def get_gsheet_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name("Credentials.json", SCOPE)
    client = gspread.authorize(creds)
    return client

def log_agent_click(agent_name):
    client = get_gsheet_client()
    sheet = client.open(SHEET_NAME).sheet1  # Using the first sheet

    # Get all existing records
    data = sheet.get_all_records()

    # Check if agent already has a row
    found = False
    for idx, row in enumerate(data, start=2):  # row 1 = header, so data starts at 2
        if row["Agent Name"] == agent_name:
            count = int(row["Count"]) + 1
            sheet.update_cell(idx, 2, count)
            found = True
            break

    if not found:
        # Append new row
        sheet.append_row([agent_name, 1])
