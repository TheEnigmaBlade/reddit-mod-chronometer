__author__ = 'Enigma'

import requests
from requests.auth import HTTPBasicAuth
import praw
from praw.errors import *

#Connection management

def init_reddit_session(config, oauth_scopes={"read", "identity"}):
	oauth_scopes = {"read", "identity"}.union(oauth_scopes)
	
	print("Connecting to reddit...", end=" ")
	# Start reddit session
	if len(config.username) == 0 or len(config.password) == 0:
		print("Username and password required")
		return None
	
	try:
		r = praw.Reddit(user_agent=config.user_agent)
		
		print("getting oauth token...", end=" ")
		client_auth = HTTPBasicAuth(config.oauth_id, config.oauth_secret)
		headers = {"User-Agent": config.user_agent}
		data = {"grant_type": "password", "username": config.username, "password": config.password}
		response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, headers=headers, data=data)
		response_content = response.json()
		if "error" in response_content and response_content["error"] != 200:
			print("failed!\nResponse code = {}".format(response_content["error"]))
			return None
		
		token = response_content["access_token"]
		if response_content["token_type"] != "bearer":
			return None
		
		print("init PRAW...", end=" ")
		r.set_oauth_app_info(config.oauth_id, config.oauth_secret, "http://example.com/unused/redirect/uri")
		r.set_access_credentials(oauth_scopes, access_token=token)
		
		print("done!")
	except praw.errors.InvalidUserPass:
		print("Failed to connect to reddit: invalid password or account")
		return None
	except Exception as e:
		print("Failed to connect to reddit, {}: {}".format(e.__class__.__name__, e))
		return None
	
	r.config.api_request_delay = 1
	r._user_agent = config.user_agent
	r._oauth_scopes = oauth_scopes
	return r

def destroy_reddit_session(r):
	r.clear_authentication()
