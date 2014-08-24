#!/usr/bin/env python

__author__ = 'Enigma'
__version__ = 1.0

import re
import praw

#Connection management

def init_reddit_session(config):
	try:
		print("Connecting to reddit...", end=" ")
		r = praw.Reddit(user_agent=config.user_agent)
		if config.username is not None:
			print("logging in...", end=" ")
			r.login(config.username, config.password)
		print("done!")
		return r
	except Exception as e:
		print("Failed to connect to reddit: {0}".format(e))
		return None

def destroy_reddit_session(r):
	r.clear_authentication()
