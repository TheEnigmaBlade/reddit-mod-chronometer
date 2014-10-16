from datetime import date

# Reddit connection info
user_agent = "Mod Chronometer, run by REDDIT_USERNAME"
username = "REDDIT_USERNAME"					# Reddit account with mod access to your subreddit
password = "REDDIT_PASSWORD"					# ^'s account password

# Bot configuration
subreddit			= "SUBREDDIT"						# Subreddit from which the mod log is being accessed
data_file			= "chronodata_{subreddit}.csv"		# File for resulting data, in the CSV format. Can use {subreddit}, {start_date}, {end_date}, and {include_lazy} to format dynamically.
start_date			= date(2014, 8, 24)					# Start date, inclusive, going backwards in time: date(YYYY, MM, DD); NOTE: start_date >= end_date, otherwise nothing will be counted
end_date			= date(2014, 7, 24)					# End date, inclusive, going backwards in time: date(YYYY, MM, DD)
include_lazy		= False								# Include mods with no actions
exclusions			= ["AutoModerator"]					# Users to exclude, like bots (not case-sensitive)
action_types		= ["removelink", "removecomment"]	# Action types to count in addition to the total, see "type": http://www.reddit.com/dev/api#GET_about_log
action_exclusions	= []								# Action types to exclude from the total (does not override action_types)
