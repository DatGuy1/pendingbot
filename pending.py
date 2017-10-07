from wikitools import *
import json
import re
import threading
import thread
import time
import datetime

site = wiki.Wiki()
site.login('DatBot','redacted')
update = page.Page(site, 'Template:Pending Changes backlog')
template_path = "/data/project/datbot/Tasks/pendingbacklog/template.txt"
LogActive = False

def normTS(ts): # normalize a timestamp to the API format
        ts = str(ts)
        if 'Z' in ts:
                return ts
        ts = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S")
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ")

def logFromAPI(lasttime):
    lasttime = normTS(lasttime)
    params = {'action':'query',
              'list':'oldreviewedpages',
              'orstart':lasttime,
              'ordir':'newer',
    }
    req = api.APIRequest(site, params)
    res = req.query(False)
    rows = res['query']['oldreviewedpages']
    #if len(rows) > 0:
        #del rows[0] # The API uses >=, so the first row will be the same as the last row of the last set
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

def getStart():
    params = {'action':'query',
              'list':'oldreviewedpages',
              'orlimit':'1',
    }
    req = api.APIRequest(site, params)
    res = req.query(False)
    row = res['query']['oldreviewedpages'][0]
    lasttime = row['pending_since']
    lastid = row['revid']
    return (lasttime, lastid)

def startAllowed(override):
        if override:
                return True
        start = page.Page(site, 'User:DatBot/task2')
        if start == "Run":
                return True
        else:
                return False

def main():
    global LogActive
    sc = StartupChecker()
    sc.start()
    (lasttime, lastid) = getStart()
    LogActive = True
    xyz = 0
    while xyz < 1:
        if useAPI:
            rows = logFromAPI(lasttime)
            amount = len(rows)
            print amount
            if is_edit_necessary(update, amount):
                update_template(update, amount)
            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("[{}] No edit necessary.".format(timestamp))
            xyz = 1
            time.sleep(1800)
            xyz = 0
""" Some code here is Enterprisey's:
The MIT License (MIT)

Copyright (c) 2015 APerson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

def pages_to_level(amount):
    if amount <= 5:
        return 5
    elif amount <= 10:
        return 4
    elif amount <= 20:
        return 3
    elif amount <= 30:
        return 2
    else:
        return 1

def is_edit_necessary(update, amount):
        current_lvl = pages_to_level(amount)
        onwiki_level_match = re.search("level\s*=\s*(\d+)",
                                       update.getWikiText())
        if onwiki_level_match:
                onwiki_level = int(onwiki_level_match.group(1))
                return onwiki_level != current_lvl
        else:
                return True

def update_template(update, amount):
        level = pages_to_level(amount)
        try:
                template = open(template_path)
        except IOError as e:
                print(e)
        else:
                try:
                    template_page.text = template.read() % (level, amount)
                    template_page.save(COMMENT % (level, int(amount)))
                except Exception as e:
                    print(e)
                finally:
                    template.close()
        
if __name__ == "__main__":
        main()
