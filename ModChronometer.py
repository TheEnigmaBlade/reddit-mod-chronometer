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

# Set up some settings
user_exclusions = list(map(str.lower, config.exclusions))

# Init storage and data
def create_action_dict():
	d = ordered_dict((at, 0) for at in config.action_types)
	d["Total"] = 0
	return d

buckets = [dict() for n in range(24)]
if config.include_lazy:
	mods = sub.get_moderators()
	for mod in mods:
		if not mod in user_exclusions:
			for h in range(len(buckets)):
				buckets[h][mod.name] = create_action_dict()

def inc_bucket(time_struct, user, action):
	hour = time_struct[3]
	bucket = buckets[hour]
	
	# Add bucket if missing
	if not user in bucket:
		bucket[user] = create_action_dict()
	
	# Inc total if not excluded
	if not action in config.action_exclusions:
		bucket[user]["Total"] += 1
	
	# Inc action type
	if action in config.action_types:
		bucket[user][action] += 1

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
		types = create_action_dict().keys()
		
		# Output actions sorted hour and moderator
		f.write("-----\n\n")
		f.write("Raw\n")
		f.write("Mod")
		for t in types:
			f.write(",{}".format(t))
		f.write("\n\n")
		
		for h in range(len(buckets)):
			f.write("{}\n".format(h))
			
			total = create_action_dict()
			for name in buckets[h]:
				user_data = buckets[h][name]
				f.write(name)
				for t in types:
					f.write(",{}".format(user_data[t]))
					total[t] += user_data[t]
				f.write("\n")
			
			totals.append(total)
			for t in types:
				f.write(",{}".format(total[t]))
			f.write("\n\n")
		
		# Output action totals sorted by hour
		f.write("-----\n\n")
		f.write("Hour totals\n")
		f.write("Hour")
		for t in types:
			f.write(",{}".format(t))
		f.write("\n\n")
		
		for h in range(len(totals)):
			total = totals[h]
			f.write(str(h))
			for t in types:
				f.write(",{}".format(total[t]))
			f.write("\n")

print("Done!")
