# coding=utf-8

import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
from sqlalchemy import create_engine
from datetime import datetime
from dask import delayed as delay
# import ipdb

def fetch_rds_mysql(query, params={}):
    """Creates connection to mysql db with sqlaclhemy and returns the results of the query passed as an argument.
    The optionnal 2nd argument allows string interpolation inside the query."""
    mysql_conn = load_connection('rds_mysql')
    engine = create_engine(mysql_conn)
    try:
        engineCon = engine.connect()
        df = pd.read_sql_query(query, engineCon, params=params)
    finally:
        engineCon.close()
    return df

@delay
def lazy_fetch_rds_mysql(query, params={}):
    """Creates connection to mysql db with sqlaclhemy and returns the results of the query passed as an argument.
    The optionnal 2nd argument allows string interpolation inside the query."""
    mysql_conn = load_connection('rds_mysql')
    engine = create_engine(mysql_conn)
    try:
        engineCon = engine.connect()
        df = pd.read_sql_query(query, engineCon, params=params)
    finally:
        engineCon.close()
    return df

def dask_fetch_rds_mysql_table(table, id_col, nb_partitions):
    """Returns a dask dataframe, you must specify rds table name, an indexed orderable column (datetime, int),
    and the number of partitions (>number of cores on the machine)."""
    mysql_conn = load_connection('rds_mysql')
    dask_df = ddf.read_sql_table(table, mysql_conn, index_col=id_col, npartitions=nb_partitions)
    return dask_df

def push_rds_mysql_table(engine, df, table):
    try:
        engineCon = engine.connect()
        df = df.to_sql(table, engineCon, index=False, if_exists='append')
    finally:
        engineCon.close()
    return df

max_results_per_city = 300
city_set = ["Montréal%2C+QC"]
positions = ["data+scientist", "data+analyst"]
columns = ["city", "job_title", "company_name", "location", "summary", "salary"]
sample_df = pd.DataFrame(columns = columns)


#scraping code:
timestamp = datetime.now()
for position in positions:
    for city in city_set:
        for start in range(0, max_results_per_city, 1):
            # https://ca.indeed.com/jobs?q=data+scientist&l=Montr%C3%A9al%2C+QC
            page = requests.get('https://ca.indeed.com/jobs?q='+ str(position) + '&l=' + str(city) + '&start=' + str(start))
            time.sleep(1)  #ensuring at least 1 second between page grabs
            soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
            # with open('soup.txt', 'w') as p:
            #     p.write(soup)

            # for div in soup.find_all(name="div", attrs={"class":"row"}):
            for div in soup.find_all(name="div", attrs={"class":"jobsearch-SerpJobCard"}):
                #specifying row num for index of job posting in dataframe
                num = (len(sample_df) + 1)
                #creating an empty list to hold the data for each posting
                job_post = []
                #append city name
                job_post.append(city)
                # grabbing job title
                for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
                    job_post.append(a["title"])
                #grabbing company name
                company = div.find_all(name="span", attrs={"class":"company"})
                if len(company) > 0:
                    for b in company:
                        job_post.append(b.text.strip())
                else:
                    sec_try = div.find_all(name="span", attrs={"class":"result-link-source"})
                    for span in sec_try:
                        job_post.append(span.text)
                #grabbing location name
                c = div.findAll(name='div', attrs={'class': 'location'})
                if c == []:
                    job_post.append('Montreal, QC')
                else:
                    for div_loc in c:
                        job_post.append(div_loc.text)
                #grabbing summary text
                d = div.findAll('span', attrs={'class': 'summary'})
                for span in d:
                    job_post.append(span.text.strip())
                #grabbing salary
                try:
                    job_post.append(div.find('nobr').text)
                except:
                  # try:
                  #     div_two = div.find(name="div", attrs={"class":"sjcl"})
                  #     div_three = div_two.find("div")
                  #     job_post.append(div_three.text.strip())
                  # except:
                    job_post.append("Nothing_found")
                #appending list of job post info to dataframe at index num
                sample_df.loc[num] = job_post

    jobs_reduced = sample_df.drop_duplicates()
    jobs_reduced['ts'] = timestamp
    jobs_reduced['position'] = position.replace('+', ' ')
    jobs_reduced['source'] = 'indeed'
    #
    # saving sample_df as a local csv file - define your own local path to save contents
    # sample_df.to_csv("[filepath].csv", encoding='utf-8')
    rds_connection = 'mysql+mysqldb://baptiste:baptiste86@persoinstance.cy0uxhmwetgv.us-east-1.rds.amazonaws.com:3306/jobs_db?charset=utf8'
    rds_engine = create_engine(rds_connection)
    push_rds_mysql_table(rds_engine, jobs_reduced, 'indeed' )
