import sys
import argparse
import re

import requests
from pprint import pprint

import datetime

import google_cal_functions

def read_file(filename):
    """Read the contents of a file and return it as a string."""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None


def main():
    print("This script is intended to be run as a module, not directly.")


def is_in_qxx_format(qxx):
    """Check if the quarter format is valid."""
    qxx_to_check = qxx.strip().upper()    
    if not re.match(r"^[WSMF]\d{2}$", qxx_to_check):
        print(f"Invalid quarter format: {qxx}. Should start with W,S,M or F followed by a two digit year")             
        return False
    return True

def qxx_to_yyyyq(qxx):
    """Convert qxx format to yyyyq format."""
    if not is_in_qxx_format(qxx):
        raise ValueError(f"Invalid quarter format: {qxx}")
    
    q_to_num = {'W': '1', 'S': '2', 'M': '3', 'F': '4'}
    
    century = '20' if qxx[1] < '5' else '19'  # Determine century based on the second character
    return f"{century}{qxx[1:3]}{q_to_num[qxx[0].upper()]}"
   
# Sample return value from get_quarter function   
# [
#   {
#     "quarter": "20254",
#     "qyy": "F25",
#     "name": "FALL 2025",
#     "category": "FALL",
#     "academicYear": "2025-2026",
#     "firstDayOfClasses": "2025-09-25T00:00:00",
#     "lastDayOfClasses": "2025-12-05T00:00:00",
#     "firstDayOfFinals": "2025-12-06T00:00:00",
#     "lastDayOfFinals": "2025-12-12T00:00:00",
#     "firstDayOfQuarter": "2025-09-21T00:00:00",
#     "lastDayOfSchedule": "2026-01-04T00:00:00",
#     "pass1Begin": "2025-05-12T09:00:00",
#     "pass2Begin": "2025-05-19T09:00:00",
#     "pass3Begin": "2025-09-08T09:00:00",
#     "feeDeadline": "2025-09-15T00:00:00",
#     "lastDayToAddUnderGrad": "2025-10-15T00:00:00",
#     "lastDayToAddGrad": "2025-12-05T00:00:00",
#     "lastDayThirdWeek": null
#   }
# ]
   
    
def get_quarter(yyyyq, UCSB_API_CONSUMER_KEY):
    """Get the quarter from yyyyq format."""
    if not re.match(r"^\d{4}[1234]$", yyyyyq):
        raise ValueError(f"Invalid yyyyq format: {yyyyyq}")

    ENDPOINT = f"https://api.ucsb.edu/academics/quartercalendar/v1/quarters?quarter={yyyyq}"

    headers = {
        "accept": "application/json",
        "ucsb-api-version": "1.0",
        "ucsb-api-key": UCSB_API_CONSUMER_KEY
    }

    response = requests.get(ENDPOINT, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from UCSB API: {response.status_code} - {response.text}") 
    data = response.json()
    
    return data

    
def get_quarter_start_dates(quarter):
     # Is the first day of classses on a Thursday or a Monday?
     first_day_of_classes = quarter['firstDayOfClasses']
     first_day_of_classes_datetime = datetime.datetime.fromisoformat(first_day_of_classes)
     first_day_of_quarter = quarter['firstDayOfQuarter']
     first_day_of_quarter_datetime = datetime.datetime.fromisoformat(first_day_of_quarter)
     
    

     first_day_of_classes_weekday = first_day_of_classes_datetime.weekday()
     if first_day_of_classes_weekday not in [0, 3]:
         raise ValueError(f"First day of classes {first_day_of_classes} is not on a Monday or Thursday.")
     if first_day_of_classes_weekday == 3:
         num_weeks = 11
         start_week = 0
     else:
         num_weeks = 10
         start_week = 1  

     start_first_week = first_day_of_quarter_datetime
     # If the first day of the quarter is not a Sunday, adjust to the previous Sunday
     if start_first_week.weekday() != 6:
        start_first_week -= datetime.timedelta(days=start_first_week.weekday() + 1)
     
     return {
         "start_week": start_week,
         "num_weeks": num_weeks,
         "start_first_week_date": start_first_week.timestamp(),
         "first_day_of_classes": first_day_of_classes_datetime.timestamp()
     }
          

    
   
if __name__=="__main__":
    
    UCSB_API_CONSUMER_KEY = read_file("UCSB_API_CONSUMER_KEY")
    if UCSB_API_CONSUMER_KEY is None:
        print("UCSB_API_CONSUMER_KEY not found. Please create a file named UCSB_API_CONSUMER_KEY with your API key.")
        sys.exit(1)
    UCSB_API_CONSUMER_KEY = UCSB_API_CONSUMER_KEY.strip()
    print(f"Using UCSB_API_CONSUMER_KEY: [{UCSB_API_CONSUMER_KEY}]")
    
    parser = argparse.ArgumentParser(description="Process quarter argument.")
    parser.add_argument("-q", "--quarter", type=str, help="Quarter (e.g., qxx)")
    args = parser.parse_args()

    qxx = args.quarter
    if not qxx:
        done = False
        while not done:
            qxx = input("Enter quarter in qxx format (e.g., F25): ")
            done = is_in_qxx_format(qxx)

    yyyyyq = qxx_to_yyyyq(qxx)
    quarter = get_quarter(yyyyyq, UCSB_API_CONSUMER_KEY)[0]
    print(f"Quarter data for {yyyyyq}: ")
    pprint(quarter)
    

    start_dates = get_quarter_start_dates(quarter)

    service = google_cal_functions.get_calendar_service()

    first_week = start_dates['start_week']
    last_week = first_week + start_dates['num_weeks'] - 1
    week_start_date = datetime.datetime.fromtimestamp(start_dates['start_first_week_date'])
    for week in range(first_week, last_week + 1):
      
        week_end_date = week_start_date + datetime.timedelta(days=6)
        print(f"Week {week} start date: {week_start_date}")
        week_event = google_cal_functions.create_multi_day_event(
            f"{qxx} Week {week}",
            week_start_date.date(),
            week_end_date.date()
        )
        google_cal_functions.add_event(service, "primary", week_event)
        # Move to the next week 
        week_start_date += datetime.timedelta(weeks=1)

    # Create events for important dates
    important_dates = [
        (f'{qxx} Fee Deadline', quarter['feeDeadline']),
        (f'{qxx} First Day of Classes', quarter['firstDayOfClasses']),
        (f'{qxx} First Day of Finals', quarter['firstDayOfFinals']),
        (f'{qxx} Last Day of Classes', quarter['lastDayOfClasses']),
        (f'{qxx} Last Day of Finals', quarter['lastDayOfFinals']),
        (f'{qxx} Last Day of Schedule', quarter['lastDayOfSchedule']),
        (f'{qxx} Last Day to Add Undergrad', quarter['lastDayToAddUnderGrad']),
        (f'{qxx} Last Day to Add Grad', quarter['lastDayToAddGrad']),
        (f'{qxx} Pass 1 Begin', quarter['pass1Begin']),
        (f'{qxx} Pass 2 Begin', quarter['pass2Begin']),
        (f'{qxx} Pass 3 Begin', quarter['pass3Begin']),
        (f'{qxx} First Day of Quarter', quarter['firstDayOfQuarter']),
    ]

    for event_name, event_date in important_dates:
        if event_date is None:
            print(f"Skipping event {event_name} as the date is None.")
            continue
        print(f"Creating event: {event_name} on {event_date}")
        event = google_cal_functions.create_all_day_event(
            event_name,
            datetime.datetime.fromisoformat(event_date).date()
        )
        result = google_cal_functions.add_event(service, "primary", event)
        if result:
            print(f"Event created: {result.get('htmlLink')}")
        else:
            print(f"Failed to create event: {event_name}")




   
