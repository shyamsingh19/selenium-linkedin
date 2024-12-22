import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def add_data_to_sheet():
    """Shows basic usage of the Sheets API.
    Appends data to a sample spreadsheet.
    """

    # Update the scope to allow writing to the spreadsheet.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # The ID and range of the sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1-pGW-36Oj28X0dyTwm1ZoeHhQpuP1tSamcdCg25Y2MI"
    SAMPLE_RANGE_NAME = "Sheet4!A2:E"  # Adjust sheet name and range as needed
    
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Prepare the data to append
        values_to_append = [
            ["New Name", "New Major"]  # Example data to append (replace with your own)
        ]

        # Call the Sheets API to append the data
        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=SAMPLE_RANGE_NAME,
                valueInputOption="RAW",  # Use "RAW" or "USER_ENTERED" based on your preference
                insertDataOption="INSERT_ROWS",  # Insert new rows
                body={"values": values_to_append},
            )
        )
        response = request.execute()

        print(f"Data appended: {response}")

    except HttpError as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    add_data_to_sheet()
