from datetime import date

# Reddit connection info
user_agent = "Mod Chronometer, run by REDDIT_USERNAME"
username = "REDDIT_USERNAME"					# Reddit account with mod access to your subreddit
password = "REDDIT_PASSWORD"					# ^'s account password

# Bot configuration
subreddit		= "SUBREDDIT"						# Subreddit from which the mod log is being accessed
data_file		= "chronodata_2014_07-08.csv"		# File for resulting data, in the CSV format
start_date		= date(2014, 8, 24)					# Start date, inclusive, going back in time: date(YYYY, MM, DD)
end_date		= date(2014, 7, 24)					# End date, inclusive, going back in time: date(YYYY, MM, DD)
exclusions		= ["AutoModerator"]					# Users to exclude, like bots (not case-sensitive)
action_types	= ["removelink", "removecomment"]	# Action types to split from the total, see "type": http://www.reddit.com/dev/api#GET_about_log
