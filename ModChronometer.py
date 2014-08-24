#!/usr/bin/env python

__author__ = 'Enigma'
__version__ = 1.0

from time import gmtime
from datetime import date
from requests.exceptions import HTTPError

from Util import *
from RedditUtil import *
import config

# Create connection to reddit
r = init_reddit_session(config)
sub = r.get_subreddit(config.subreddit, fetch=False)

# Init storage and data
buckets = []
for hour in range(24):
	buckets.append({})

def inc_bucket(time_struct, user, action):
	hour = time_struct[3]
	bucket = buckets[hour]
	
	# Add bucket if missing
	if not user in bucket:
		bucket[user] = [0, 0, 0]
	
	# Inc total
	bucket[user][2] += 1
	# Inc action type
	# For types, see: http://www.reddit.com/dev/api#GET_about_log
	for case in switch(action):
		if case("removelink"):
			bucket[user][0] += 1
			break
		if case("removecomment"):
			bucket[user][1] += 1
			break

user_exclusions = list(map(str.lower, config.exclusions))

# Go!
done = False
successful = False
last = None
last_time = -1
count = 0

try:
	while not done:
		log = sub.get_mod_log(limit=100, params={"after": last})
		for log_entry in log:
			created_utc = log_entry.created_utc
			time_utc = gmtime(created_utc)
			date_utc = date(time_utc[0], time_utc[1], time_utc[2])
			
			# Check if the ending date has been reached
			if date_utc >= config.end_date:
				# If we've reached the start, record the entry
				if date_utc <= config.start_date and not log_entry.mod.lower() in user_exclusions:
					inc_bucket(time_utc, log_entry.mod, log_entry.action)
			# If it has, we're done!
			else:
				done = True
				break
			
			# Check if the last known action (I don't trust the API's ordering)
			if log_entry.target_fullname is not None and (created_utc < last_time or last_time < 0):
				last = log_entry.id
				last_time = created_utc
		
		count += 100
		last_date = gmtime(last_time)
		print("On {}/{}/{}: {} parsed".format(last_date[1], last_date[2], last_date[0], count))
	
	successful = True

# Don't have permission to view the log
except (praw.errors.ModeratorRequired, praw.errors.ModeratorOrScopeRequired, HTTPError) as e:
	code = e.response.status_code
	if not isinstance(e, HTTPError) or code == 403:
		print("Error: Mod authorization lost")
	elif isinstance(e, HTTPError):
		print("Error: Failed to load page, {} ({}) returned by server".format(code, e.response))
# Couldn't connect to reddit
except ConnectionError as e:
	print("Error: Connection failed, {}".format(e))

destroy_reddit_session(r)

# Output
if successful:
	print("Saving data to {}".format(config.data_file))
	with open(config.data_file, "w+") as f:
		f.write("/r/{}\n"	.format(config.subreddit))
		f.write("{},{}\n\n"	.format(config.start_date, config.end_date))
		
		totals = []
		
		# Output actions sorted hour and moderator
		f.write("-----\n\n")
		f.write("Raw\n")
		f.write("Mod,removelink,removecomment,Total\n\n")
		
		for hour in range(len(buckets)):
			f.write("{}\n".format(hour))
			
			total = [0, 0, 0]
			for name in buckets[hour]:
				user_data = buckets[hour][name]
				f.write("{},{},{},{}\n".format(name, user_data[0], user_data[1], user_data[2]))
				
				for c in range(len(total)):
					total[c] += user_data[c]
			
			f.write(",{},{},{}\n\n".format(total[0], total[1], total[2]))
			totals.append(total)
		
		# Output action totals sorted by hour
		f.write("-----\n\n")
		f.write("Hour totals\n")
		f.write("Hour,removelink,removecomment,Total\n\n")
		
		for hour in range(len(totals)):
			total = totals[hour]
			f.write("{},{},{},{}\n".format(hour, total[0], total[1], total[2]))

print("Done!")
