import togglRound as tr
from datetime import datetime
import pytz

now = datetime.utcnow()
utc = pytz.utc

def test_07MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 7, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_08MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 8, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 15, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_22MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 22, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 15, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_23MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 23, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 30, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_37MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 37, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 30, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_38MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 38, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 45, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_52MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 52, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 45, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_53MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 53, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour + 1, 0, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_53After23HoursRoundsToNextDay():
    tmpDt = datetime(now.year, now.month, now.day, 23, 53, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day + 1, 0, 0, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_53After23HoursAtEndOfMonthRoundsToNextMonth():
    tmpDt = datetime(now.year, 1, 31, 23, 53, tzinfo=utc)
    expected = datetime(now.year, 2, 1, 0, 0, tzinfo=utc)
    assert(tr.roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_lessThanEightHoursCreatesAdminTime():
    start = datetime(now.year, 1, 31, 7, 0, tzinfo=utc)
    end = datetime(now.year, 1, 31, 12, 0, tzinfo=utc)
    entry = tr.TimeEntry(start=start.isoformat(), stop=end.isoformat(), duration=18000)

    expected_admin_start = datetime(now.year, 1, 31, 12, 0, tzinfo=utc)
    expected_admin_stop = datetime(now.year, 1, 31, 15, 0, tzinfo=utc)
    admin_entry = tr.fillWithAdminTime([entry])[0]
    assert(admin_entry.start == expected_admin_start)
    assert(admin_entry.duration == 10800)
    assert(admin_entry.stop == expected_admin_stop)

def test_lessThanEightHoursCreatesAdminTimeMultiDay():
    start = datetime(now.year, 1, 31, 7, 0, tzinfo=utc)
    end = datetime(now.year, 1, 31, 12, 0, tzinfo=utc)
    entries = []
    entries.append(tr.TimeEntry(start=start.isoformat(), stop=end.isoformat(), duration=18000))

    start = datetime(now.year, 2, 1, 7, 0, tzinfo=utc)
    end = datetime(now.year, 2, 1, 12, 0, tzinfo=utc)
    entries.append(tr.TimeEntry(start=start.isoformat(), stop=end.isoformat(), duration=18000))

    expected = [
        tr.TimeEntry(
            start=datetime(now.year, 1, 31, 12, 0, tzinfo=utc).isoformat(),
            stop=datetime(now.year, 1, 31, 15, 0, tzinfo=utc).isoformat(),
            duration=10800),
        tr.TimeEntry(
            start=datetime(now.year, 2, 1, 12, 0, tzinfo=utc).isoformat(),
            stop=datetime(now.year, 2, 1, 15, 0, tzinfo=utc).isoformat(),
            duration=10800),
    ]

    actual_entries = tr.fillWithAdminTime(entries)
    for actual, expected in zip(actual_entries, expected):
        assert(actual.start == expected.start)
        assert(actual.duration == expected.duration)
        assert(actual.stop == expected.stop)


def test_greaterThanEightHoursHasNoAdminTime():
    start = datetime(now.year, 1, 31, 7, 0, tzinfo=utc)
    end = datetime(now.year, 1, 31, 16, 0, tzinfo=utc)
    entries = []
    diff = end - start
    entries.append(tr.TimeEntry(start=start.isoformat(), stop=end.isoformat(), duration=diff.total_seconds()))

    actual_entries = tr.fillWithAdminTime(entries)
    assert(len(actual_entries) == 0)

def test_runningTimerDoesNotCreateAdminTime():
    start = datetime(now.year, 1, 31, 7, 0, tzinfo=utc)
    entries = []
    entries.append(tr.TimeEntry(start=start.isoformat()))

    actual_entries = tr.fillWithAdminTime(entries)
    assert(len(actual_entries) == 0)

def test_negativeDurationDoesNotCreateAdminTime():
    start = datetime(now.year, 1, 31, 7, 0, tzinfo=utc)
    entries = []
    entries.append(tr.TimeEntry(start=start.isoformat(), duration=-1544631140))

    actual_entries = tr.fillWithAdminTime(entries)
    assert(len(actual_entries) == 0)

# Need to go back two weeks and ensure that no more than 40 hours per week exist
# before adding Admin time