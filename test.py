from togglRound import roundToQuarterHour
from datetime import datetime
import pytz

now = datetime.utcnow()
utc = pytz.utc

def test_06MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 6, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_08MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 8, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 15, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_22MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 22, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 15, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_23MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 23, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 30, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_36MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 36, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 30, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_38MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 38, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 45, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_52MinutesRoundsDown():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 52, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour, 45, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_53MinutesRoundsUp():
    tmpDt = datetime(now.year, now.month, now.day, now.hour, 53, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day, now.hour + 1, 0, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_53After23HoursRoundsToNextDay():
    tmpDt = datetime(now.year, now.month, now.day, 23, 53, tzinfo=utc)
    expected = datetime(now.year, now.month, now.day + 1, 0, 0, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())

def test_53After23HoursAtEndOfMonthRoundsToNextMonth():
    tmpDt = datetime(now.year, 1, 31, 23, 53, tzinfo=utc)
    expected = datetime(now.year, 2, 1, 0, 0, tzinfo=utc)
    assert(roundToQuarterHour(tmpDt).isoformat() == expected.isoformat())






