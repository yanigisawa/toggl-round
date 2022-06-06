import json
import requests
import os
import sys
from dateutil.parser import parse
from datetime import datetime, timedelta, date
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
    def __init__(self, start = None, stop = None, duronly = None, pid = None,
            billable = None, guid = None, at = None, wid = None,
            id = None, uid = None, description=None, duration=None, tags=None):
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
        # return "{0} - {1} - {2}".format(self.start, getattr(self, 'stop', None), self.duration)
        return "{0}".format(self.__dict__)

def getHeaders():
    api_key = os.environ.get("TOGGL_API_KEY")
    if not api_key:
        print("'TOGGL_API_KEY' environment variable not set. Please set this variable to continue")
        return

    base64Token = base64.b64encode("{0}:api_token".format(api_key).encode()).decode()
    return { "Authorization" : "Basic " + base64Token }

def getTimeEntries(startDate = None, endDate = None):
    headers = getHeaders()
    url = "https://api.track.toggl.com/api/v8/time_entries"
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
    print("JSON: {0}".format(resp.json()))
    for e in resp.json():
        entry = TimeEntry(**e)
        entries.append(entry)

    return entries

def getLastTimeForDay(date_string, entries):
    latest_date = datetime(1987, 1, 31, 12, 0, tzinfo=pytz.utc)
    dt = parse(date_string)
    day_entries = sorted([e for e in entries if e.start.date() == dt.date()], key=lambda x: x.start)
    for e in day_entries:
        if hasattr(e, 'stop') and e.stop > latest_date:
            latest_date = e.stop
    if latest_date == date.min:
        return None
    return latest_date

def get_time_per_day(entries):
    time_per_day = {}
    for e in entries:
        date_key = e.start.date().isoformat()
        if date_key not in time_per_day.keys():
            time_per_day[date_key] = e.duration
            continue
        time_per_day[date_key] += e.duration
    return time_per_day

def fillWithAdminTime(entries):
    now = datetime.now()
    utc = pytz.utc
    # import pdb; pdb.set_trace()
    time_per_day = get_time_per_day(entries)

    admin_entries = []
    eight_hours_in_seconds = 28800
    for date, duration in time_per_day.items():
        if duration < eight_hours_in_seconds:
            admin_duration = eight_hours_in_seconds - duration
            start = getLastTimeForDay(date, entries)
            te = TimeEntry(
                start=start.isoformat(),
                stop=roundToQuarterHour(start + timedelta(seconds=admin_duration)).isoformat(),
                wid=876389, pid=12780480, description='Admin')

            admin_entries.append(te)

    print('Would create Admin: {0}'.format(admin_entries))
    return admin_entries

def updateEntries(entries):
    headers = getHeaders()
    for e in entries:
        url = "https://api.track.toggl.com/api/v8/time_entries/{0}".format(e.id)
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
    # TODO - have not tested the Admin Time feature
    # admin_entries = fillWithAdminTime(entries)
    # updateEntries(admin_entries)
    print("Update Complete")

if __name__ == "__main__":
    # entries = getTimeEntries()
    # fillWithAdminTime(entries)
    # for e in entries:
    #     print(e)
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
