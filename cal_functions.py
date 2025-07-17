import sys
import argparse
import re

import requests
from pprint import pprint

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
    quarter = get_quarter(yyyyyq, UCSB_API_CONSUMER_KEY)
    print(f"Quarter data for {yyyyyq}: ")
    pprint(quarter)
