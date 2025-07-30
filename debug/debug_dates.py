#!/usr/bin/env python3

from datetime import datetime, timedelta

today = datetime.now()
print('Today:', today.strftime('%Y-%m-%d'))

start_next = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
end_next = (today.replace(day=28) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

print('Next month start:', start_next.strftime('%Y-%m-%d'))
print('Next month end:', end_next.strftime('%Y-%m-%d'))

# Simple approach
simple_start = datetime(2025, 8, 1)
simple_end = datetime(2025, 8, 31, 23, 59, 59)

print('Simple start:', simple_start.strftime('%Y-%m-%d'))
print('Simple end:', simple_end.strftime('%Y-%m-%d'))
