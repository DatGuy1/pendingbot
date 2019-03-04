from wikitools import *
import json
import re
import threading
import sys
import thread
import time
import datetime
import userpass

site = wiki.Wiki()
site.login(userpass.username, userpass.password)
update = page.Page(site, 'User:DatBot/pendingbacklog')
template_path = "/data/project/datbot/Tasks/pendingbacklog/template.txt"
useAPI = True
LogActive = False

def logFromAPI():
	params = {'action':'query',
		'list':'oldreviewedpages',
		'orlimit':'max',
		'ordir':'newer',
	}
	req = api.APIRequest(site, params)
	res = req.query(False)
	rows = res['query']['oldreviewedpages']
	ret = []
	for row in rows:
		entry = {}
		entry['p'] = row['pageid']
		entry['revid'] = row['revid']
		entry['pending_since'] = row['pending_since']
		ret.append(entry)
	return ret

class StartupChecker(threading.Thread):
	def run(self):
		global LogActive
		time.sleep(60)
		if not LogActive:
			print "Init fail"
			thread.interrupt_main()

def startAllowed():
	startpage = page.Page(site, 'User:DatBot/Pending backlog/Run')
	start = startpage.getWikiText()
	if start == "Run":
		return True
	else:
		return False

def main():
	global LogActive
	sc = StartupChecker()
	sc.start()
	LogActive = True
	startAllowed()
	xyz = 0
	while xyz < 1:
		if useAPI:
			rows = logFromAPI()
			amount = len(rows)
			if is_edit_necessary(update, amount):
				update_template(update, amount)
			else:
				pass
			xyz = 1
			time.sleep(900)
			xyz = 0

""" Some code here is Enterprisey's:
The MIT License (MIT)

Copyright (c) 2015 APerson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

def pages_to_level(amount):
	if amount <= 3:
		return 5
	elif amount <= 7:
		return 4
	elif amount <= 12:
		return 3
	elif amount <= 17:
		return 2
	else:
		return 1

def is_edit_necessary(update, amount):
	current_lvl = pages_to_level(amount)
	onwiki_amount_match = re.search("info\s*=\s*(\d+)", update.getWikiText())
	if onwiki_amount_match:
		onwiki_amount = int(onwiki_amount_match.group(1))
		return onwiki_amount != amount
	else:
		return True

def update_template(update, amount):      
	level = pages_to_level(amount)
	template = open(template_path)
	change = template.read() % (level, amount)
	editsummary = "[[Wikipedia:Bots/Requests for approval/DatBot 4|Bot]] updating pending changes level to level %d (%d pages)" % (level, int(amount))
	update.edit(text=change, summary=editsummary, bot=True)
	template.close()

if __name__ == "__main__":
	main()
