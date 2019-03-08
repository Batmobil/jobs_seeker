import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer



from dask import delayed as delay
from datetime import datetime as dt
import pandas as pd
from sqlalchemy import create_engine
# fetch data from DB.
@delay
def lazy_fetch_rds_mysql(engine, query, params={}):
    """Creates connection to mysql db with sqlaclhemy and returns the results of the query passed as an argument.
    The optionnal 2nd argument allows string interpolation inside the query."""
    try:
        engineCon = engine.connect()
        df = pd.read_sql_query(query, engineCon, params=params)
    finally:
        engineCon.close()
    return df


# Load Data.
start_date = dt(2019, 1, 1)
end_date = dt.now()
query_jobs_data = """SELECT * FROM indeed WHERE ts >= %(start)s AND ts < %(end)s """
rds_connection = 'mysql+mysqldb://baptiste:baptiste86@persoinstance.cy0uxhmwetgv.us-east-1.rds.amazonaws.com:3306/jobs_db?charset=utf8'
rds_engine = create_engine(rds_connection)
jobs_data = lazy_fetch_rds_mysql(rds_engine, query_jobs_data, params={'start': start_date, 'end': end_date})
jobs_df = jobs_data.compute()

# Taking a sample to test program.
ex = jobs_df.loc[:, 'summary']
ex = ex.drop_duplicates()
all_words =[]
for description in ex:

    # Tokenizing
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(description.lower())

    # Removing stop words.
    stop_words = set(stopwords.words('english'))
    words = [word for word in tokens if word not in stop_words]

    print(words)
    all_words.extend(words)

text = nltk.Text(all_words)
# Calculate Frequency distribution
freq = nltk.FreqDist(text)

# Print and plot most common words
print(freq.most_common(20))
# freq.plot(10)
