from datetime import datetime, timedelta

nobj = datetime.now()
now = nobj.strftime("%H:%M:%S")

time_change = timedelta(minutes=30)
lobj = nobj + time_change
later = lobj.strftime("%H:%M:%S")

print(now)
print(later)

print(later <= now)
