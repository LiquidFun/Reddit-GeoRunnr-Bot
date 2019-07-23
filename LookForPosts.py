import praw
import re
import os, sys
from datetime import datetime


def getRedditInstance():
    # Read reddit client_id and client_secret from file (to avoid accidentally publishing it)
    inputFile = open(os.path.join(os.path.dirname(__file__), "RedditAPIAccess.txt"))
    lines = []
    for line in inputFile:
        lines.append(line)
    client_id = lines[0]
    client_secret = lines[1]
    username = lines[2]
    password = lines[3]

    # Get reddit instance
    reddit = praw.Reddit(client_id=client_id.rstrip(), 
                         client_secret=client_secret.rstrip(), 
                         user_agent='linux:georunnr_bot:0.1 (by /u/LiquidProgrammer',
                         username=username.rstrip(),
                         password=password.rstrip())
    return reddit

# Get the username of the bot which is currently logged in
def getBotUsername():
    inputFile = open(os.path.join(os.path.dirname(__file__), "RedditAPIAccess.txt"))
    lines = []
    for line in inputFile:
        lines.append(line)
    return lines[2].strip()

def formula(score, mins):
	return score * (1.0 - (mins/60.0)**2.0)

def getInfoLine():
    return """

---

^(I'm a bot, message the author: /u/LiquidProgrammer if I made a mistake.)"""

def checkNewCommentsForGeoRunnr():

	# Measure time
	startTime = datetime.now()

	print(str(datetime.now()) + ": Running GeoRunnr.")

	reddit = getRedditInstance()
	subreddit = reddit.subreddit("geoguessr")

	print(str(datetime.now() - startTime) + ": Acquiring submission list. ")

	# Get last submissions from the subreddit
	# submissionList = subreddit.new(limit = 1000)

	print(str(datetime.now() - startTime) + ": Looking for posts with the !GeoRunnr tag. ")    

	botUsername = getBotUsername()
	
	# print(botUsername)

	repliedCommentIds = set()

	# Look for comments with !GeoRunnr
	for comment in subreddit.stream.comments():
		if "!georunnr" in comment.body.lower():
			alreadyReplied = False
			comment.refresh()
			for reply in comment.replies:
				try:
					if reply.author.name == botUsername:
						alreadyReplied = True
				except AttributeError:
					pass
			message = ""
			if comment.id not in repliedCommentIds and comment.author.name != botUsername and not alreadyReplied:
				repliedCommentIds.add(comment.id)
				entry = [line for line in comment.body.lower().split('\n') if "!georunnr" in line][0].split()
				if len(entry) != 3:
					entry.extend(['Not found'] * 3)
					message = """Sorry, it seems I didn't understand your entry correctly!
	It looks like `{0}` is your score and `{1}` is your time, is this correct?
	Entries should be formatted like this: `!GeoRunnr score mm:ss`.""".format(entry[1], entry[2])
				else:
					score = int(entry[1])
					timeStr = entry[2].split(":")
					time = 0

					print(entry)

					# If time is given in hh:mm:ss
					if len(timeStr) == 3: 
						time = int(timeStr[0]) * 60 + int(timeStr[1]) + int(timeStr[2]) / 60.0

					# If time is given in mm:ss
					if len(timeStr) == 2: 
						time = int(timeStr[0]) + int(timeStr[1]) / 60.0

					# If time is given in ss
					if len(timeStr) == 1: 
						time = int(timeStr[0]) / 60.0

					message = "Your !GeoRunnr score is %.2f" % formula(score, time)

				message += getInfoLine()
				print(message)
				print()

				comment.reply(message)




	# Print how long it took
	print(str(datetime.now() - startTime) + ": Finished. ")    
	print(datetime.now())

if __name__ == '__main__':
	checkNewCommentsForGeoRunnr()
