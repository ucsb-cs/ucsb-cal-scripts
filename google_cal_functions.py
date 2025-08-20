import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/calendar"]




def add_event(service, calendar_id, event):
    """Add an event to the calendar if it doesn't already exist."""
    try:
        # Check for existing events
        events = service.events().list(calendarId=calendar_id).execute()
        for existing_event in events.get("items", []):
            if existing_event.get("summary") == event["summary"]:
                print(f"Event already exists: {existing_event.get('htmlLink')}")
                return None

        # If not found, create the event
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    return created_event


def create_event(summary, start_time, end_time):
    """Create an event dictionary."""
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
    }
    return event

def create_all_day_event(summary, date):
    """Create an all-day event dictionary for Google Calendar."""
    event = {
        "summary": summary,
        "start": {
            "date": date.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "date": date.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
    }
    return event
    
def create_multi_day_event(summary, start_date, end_date):
    """Create a multi-day event dictionary for Google Calendar."""
    event = {
        "summary": summary,
        "start": {
            "date": start_date.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "date": end_date.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
    }
    return event

    
def get_calendar_service():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
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
    service = build("calendar", "v3", credentials=creds)
    # Call the Calendar API
  except HttpError as error:
    print(f"An error occurred: {error}")

  return service


if __name__ == "__main__":
  service = get_calendar_service()
  
  event = create_all_day_event("F25 - First Day Of Classes", datetime.date(2025, 9, 25))
  add_event(service, "primary", event)

  week0 = create_multi_day_event("F25 Week 0", datetime.date(2025, 9, 21), datetime.date(2025, 9, 27))
  add_event(service, "primary", week0)
  
  