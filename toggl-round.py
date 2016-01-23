import json
import requests
import os
from dateutil.parser import parse
from datetime import datetime

class TimeEntryEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, TimeEntry):
            return obj.__dict__

class TimeEntry:
    def __init__(self, description = None, tags = None, duration = None,
            start = None, stop = None, duronly = None, pid = None,
            billable = None, guid = None, at = None, wid = None, 
            id = None, uid = None):
        self.description = description
        self.tags = tags
        self.duration = duration
        self.start = self.truncateSeconds(parse(start))
        self.stop = self.truncateSeconds(parse(stop))
        self.duronly = duronly
        self.pid = pid
        self.billable = billable
        self.guid = guid
        self.at = at
        self.wid = wid
        self.id = id
        self.uid = uid

    def truncateSeconds(self, dt):
        return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, tzinfo = dt.tzinfo)

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.start, self.stop, self.duration)

def getHeaders():
    api_key = os.environ.get("TOGGL_API_KEY")
    if not api_key:
        print("'TOGGL_API_KEY' environment variable not set. Please set this variable to continue")
        return 

    base64Token = "{0}:api_token".format(api_key).encode("base64").rstrip()
    return { "Authorization" : "Basic " + base64Token }

def getTimeEntries():
    headers = getHeaders()
    resp = requests.get("https://www.toggl.com/api/v8/time_entries", headers = headers)
    entries = []
    # te = TimeEntry(**resp.json()['data'])

    for e in resp.json():
       entry = TimeEntry(**e)
       entries.append(entry)

    return entries

def roundEntries(entries):
    pass

def updateEntries(entries):
    headers = getHeaders()
    for e in entries:
        url = "https://www.toggl.com/api/v8/time_entries/{0}".format(e.id)
        te = { "time_entry" : e}
        teJson = json.dumps(te, cls = TimeEntryEncoder)
        r = requests.put(url, headers = headers, data = teJson)
        print(r.text)
        print
        # import time
        # time.sleep(1)

def main():
    entries = getTimeEntries()
    print(entries)
    roundEntries(entries)
    updateEntries(entries)

if __name__ == "__main__":
    main()
