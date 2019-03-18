####ARXIV scraper

import urllib
import time

from pprint import pprint
# Building query.
url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
for i in range(10):
     url = 'http://export.arxiv.org/api/query?search_query=ti:"nuclear simulation code"&sortBy=submittedDate&sortOrder=ascending&start={}&max_results=10'.format(i)
     data = urllib.request.urlopen(url).read()
     pprint(data)
     time.sleep(5)
