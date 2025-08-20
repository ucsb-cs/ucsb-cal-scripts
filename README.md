# ucsb-cal-scripts
Scripts that work with the UCSB Academic Calendar

Goals:
* A script that, given a Google Calendar, and a Quarter, will add all of the dates from the UCSB Academic Calendar to the Google Calendar
* Any other scripts that may prove use that work with the UCSB Academic Calendar as the source data

## Python Setup

* Create a virtual environment: `python3 -m venv venv`
* Source the virtual environment: `source venv/bin/activate`
* Install dependencies

```
pip install requests
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## To run the script:

You need:

* a UCSB_API_CONSUMER_KEY file with a key obtained from developer.ucsb.edu
* a `credentials.json` file with credentials obtained from Google Developer Console

(TODO: Add more detail to the instructions above about how to obtain these credentials)

Then run this, where `F25` is the quarter you want to add to your calendar.
```
python cal_functions.py -q F25
```