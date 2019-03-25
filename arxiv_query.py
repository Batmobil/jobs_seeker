####ARXIV scraper

import urllib
import time
import feedparser
from sqlalchemy import create_engine
import pandas as pd
import ipdb

def push_rds_mysql_table(engine, df, table):
    try:
        engineCon = engine.connect()
        df = df.to_sql(table, engineCon, index=False, if_exists='append')
    finally:
        engineCon.close()
    return df

# Base api query url
base_url = 'http://export.arxiv.org/api/query?'

# Final table to write
final_table = 'arxiv_nuc_sim_code'

# Search parameters
search_query = 'all:nuclear+simulation+code' # search for nuclear in all fields
start = 0                       # start at the first result
total_results = 10000              # want 20 total results
results_per_iteration = 5       # 5 results at a time
wait_time = 3                   # number of seconds to wait beetween calls

print('Searching arXiv for %s' % search_query)


for i in range(start,total_results,results_per_iteration):
    articles_df = pd.DataFrame()
    print("Results %i - %i" % (i,i+results_per_iteration))
    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                         i,
                                                        results_per_iteration)

    # perform a GET request using the base_url and query
    response = urllib.request.urlopen(base_url+query).read()

    # parse the response using feedparser
    feed = feedparser.parse(response)

    # Run through each entry, and print out information
    for entry in feed.entries:
#         print('arxiv-id: %s' % entry.id.split('/abs/')[-1])
        print('Title:  %s' % entry.title)
        # feedparser v4.1 only grabs the first author
        print('First Author:  %s' % entry.author)
        print(f'Published: {entry.published}')
        print("\n")
#         print('Summary:  %s' % entry.summary)
    
    # Write articles metadata to DB.
    posts = []
    for post in feed.entries:
        posts.append((post.title, post.author, post.published, post.summary))
    articles_df = pd.DataFrame(posts, columns=['title', 'author', 'published', 'summary'])
#     print(articles_df)

    rds_connection = 'mysql+mysqldb://baptiste:baptiste86@persoinstance.cy0uxhmwetgv.us-east-1.rds.amazonaws.com:3306/jobs_db?charset=utf8'
    rds_engine = create_engine(rds_connection)
    print('Appending {} rows to table.'.format(articles_df.shape[1]))
    push_rds_mysql_table(rds_engine, articles_df, final_table)
    
    # Remember to play nice and sleep a bit before you call
    # the api again!
    print('Sleeping for %i seconds' % wait_time)
    time.sleep(wait_time)
    
print('Done')


