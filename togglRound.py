import json
import requests
import os
import sys
from dateutil.parser import parse
from datetime import datetime, timedelta
import pytz
import base64
import rollbar

class TimeEntryEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, TimeEntry):
            return obj.__dict__

def truncateSeconds(dt):
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, tzinfo = dt.tzinfo)

def roundToQuarterHour(dt):
    roundTo = int((dt.minute + 7.5) / 15) * 15 
    m = roundTo - dt.minute
    return dt + timedelta(minutes = m) 

class TimeEntry:
    def __init__(self, description = None, tags = None, duration = None,
            start = None, stop = None, duronly = None, pid = None,
            billable = None, guid = None, at = None, wid = None, 
            id = None, uid = None):
        self.description = description
        self.tags = tags

        if start != None:
            self.start = roundToQuarterHour(truncateSeconds(parse(start)))

        if stop != None:
            self.stop = roundToQuarterHour(truncateSeconds(parse(stop)))

        if start != None and stop != None:
            self.duration = (self.stop - self.start).seconds
        self.duronly = duronly
        self.pid = pid
        self.billable = billable
        self.guid = guid
        self.at = at
        self.wid = wid
        self.id = id
        self.uid = uid

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.start, self.stop, self.duration)

def getHeaders():
    api_key = os.environ.get("TOGGL_API_KEY")
    if not api_key:
        print("'TOGGL_API_KEY' environment variable not set. Please set this variable to continue")
        return 

    base64Token = base64.b64encode("{0}:api_token".format(api_key).encode()).decode()
    return { "Authorization" : "Basic " + base64Token }

def getTimeEntries(startDate = None, endDate = None):
    headers = getHeaders()
    url = "https://www.toggl.com/api/v8/time_entries"
    params = {}
    if startDate != None:
        params['start_date'] = startDate.isoformat()

    if endDate != None:
        params["end_date"] = endDate.isoformat()

    resp = requests.get(url, headers = headers, params = params)
    if resp.status_code != 200:
        print("Failed to get time entries: Response: {0} - {1}".format(resp.status_code, resp.text))
        return []

    entries = []
    print("Found {0} item(s)".format(len(resp.json())))
    for e in resp.json():
        entry = TimeEntry(**e)
        entries.append(entry)

    return entries

def updateEntries(entries):
    headers = getHeaders()
    for e in entries:
        url = "https://www.toggl.com/api/v8/time_entries/{0}".format(e.id)
        te = { "time_entry" : e}
        teJson = json.dumps(te, cls = TimeEntryEncoder)
        r = requests.put(url, headers = headers, data = teJson)
        if r.status_code != 200:
            print("Failed to update time: {0}".format(r.text))
            return

def main():
    utc = pytz.utc
    yesterday = datetime.utcnow() - timedelta(days = 10)
    entries = getTimeEntries(startDate = datetime(yesterday.year,
        yesterday.month, yesterday.day, tzinfo = utc))
    updateEntries(entries)
    print("Update Complete")

if __name__ == "__main__":
    rollbar_key = os.environ.get("ROLLBAR_KEY")
    if not rollbar_key:
        print("'ROLLBAR_KEY' environment variable not set. Please set this variable to continue")
        rollbar.report_message('Missing ROLLBAR_KEY environment variable', 'error')
        sys.exit(1)
    rollbar.init(rollbar_key, 'production')
    try:
        main()
    except:
        # catch-all
        rollbar.report_exc_info()
