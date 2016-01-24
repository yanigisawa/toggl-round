# toggl-round
Round time entries entered into toggl

The Toggl iOS application automatically includes the seconds with each start and stop time. 
When entering time into a separate systems in which you need to round your time to
the nearest quarter hour, this creates uneven portions of time. (i.e. 1.26 or 3.51 hours)

This command will first truncate all of the second parts of the date time stamp of each entry,
then will round each to the nearest quarter hour. 
