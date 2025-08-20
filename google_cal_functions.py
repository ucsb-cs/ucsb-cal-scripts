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


import datetime

def add_event(service, calendar_id, event):
    """
    Adds an event to a calendar after checking for duplicates.

    Args:
        service: The Google Calendar API service object.
        calendar_id: The ID of the calendar.
        event: The event dictionary to be added.

    Returns:
        The created event object if no duplicate exists, otherwise None.
    """
    try:
        # Extract the start and end times from the event dictionary
        if 'date' in event.get('start', {}):  # All-day event
            start_time = datetime.datetime.strptime(event['start']['date'], '%Y-%m-%d').date()
            end_time = datetime.datetime.strptime(event['end']['date'], '%Y-%m-%d').date()
            time_min = datetime.datetime.combine(start_time, datetime.time.min).isoformat() + 'Z'
            time_max = datetime.datetime.combine(end_time, datetime.time.max).isoformat() + 'Z'
        else:  # Regular or multi-day event
            start_time_str = event['start']['dateTime']
            end_time_str = event['end']['dateTime']
            time_min = start_time_str
            time_max = end_time_str

        # Search for existing events with the same summary and time range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            q=event['summary'],
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Check for duplicates based on summary and start time
        for existing_event in events:
            # Check for both regular and all-day events
            if 'date' in existing_event.get('start', {}):
                existing_start_date = existing_event['start']['date']
                event_start_date = event['start'].get('date')
                if existing_event['summary'] == event['summary'] and existing_start_date == event_start_date:
                    print(f"Duplicate event found: '{existing_event['summary']}' starting on {existing_start_date}. Returning None.")
                    return None
            else:
                existing_start_time = existing_event['start']['dateTime']
                event_start_time = event['start']['dateTime']
                if existing_event['summary'] == event['summary'] and existing_start_time == event_start_time:
                    print(f"Duplicate event found: '{existing_event['summary']}' starting at {existing_start_time}. Returning None.")
                    return None
        
        # No duplicate found, so create the event
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created: '{created_event.get('summary')}'")
        return created_event

    except Exception as error:
        print(f'An error occurred: {error}')
        return None
    

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
  
  