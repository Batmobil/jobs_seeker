# Code along project
###################

# Imports.
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.offline as pyo
import plotly.graph_objs as go

from datetime import datetime as dt
# import pandas_datareader.data as web
import pandas as pd
from sqlalchemy import create_engine
from dask import delayed as delay
import dask.dataframe as ddf
import ipdb
# project import
from jobs_dashboard_callbacks import register_jobs_dashboard_callbacks
from jobs_dashboard_layout import register_jobs_dashboard_layout

# nlp imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

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
# Define app and authentication.
USERNAME_PASSWORD_PAIRS = [['baptiste', 'baptiste86']]
app = dash.Dash()
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server
app.config['suppress_callback_exceptions']=True # allow to separate the layout for each tab in separate callbacks.

######COMPUTE DATA TO PASS TO CALLBACKS.

# Count by company.
start_date = dt(2019, 1, 1)
end_date = dt.now()
query_jobs_data = """SELECT * FROM indeed WHERE ts >= %(start)s AND ts < %(end)s """
rds_connection = 'mysql+mysqldb://baptiste:baptiste86@persoinstance.cy0uxhmwetgv.us-east-1.rds.amazonaws.com:3306/jobs_db?charset=utf8'
rds_engine = create_engine(rds_connection)
jobs_data = lazy_fetch_rds_mysql(rds_engine, query_jobs_data, params={'start': start_date, 'end': end_date})
jobs_df = jobs_data.compute()
jobs_df['cnt']=1
# nsdq = nsdq.set_index('Symbol')
positions = [{'label': pos, 'value': pos} for pos in sorted(jobs_df['position'].unique().tolist())]
cities = jobs_df['city'].str.strip('%').unique().tolist()
locations = [{'label': loc.split('%2C')[0], 'value': loc} for loc in sorted(jobs_df['city'].unique().tolist())]

# count by company:
company_traces = []
companies_df = jobs_df.groupby(['city', 'company_name'])['cnt'].sum().sort_values(ascending=False)
companies = companies_df.index.get_level_values(1).tolist()
# TODO: to be corrected as now companies_df has city index as ell.
# for city in companies_df.index.get_level_values(0).tolist():
    # for company in companies:
for (city, company) in companies_df.index:
        # df = df.groupby('ts')['cnt'].sum()
    company_traces.append({'x': company, 'y': companies_df.loc[(city, company)], 'name':company})


# Word clouds data.
query_jobs_data = """SELECT * FROM indeed WHERE ts >= %(start)s AND ts < %(end)s """
rds_connection = 'mysql+mysqldb://baptiste:baptiste86@persoinstance.cy0uxhmwetgv.us-east-1.rds.amazonaws.com:3306/jobs_db?charset=utf8'
summary_ddf = ddf.read_sql_table('indeed', rds_connection, index_col='ts')
summary_ddf = summary_ddf[['city', 'position', 'summary']].reset_index()
summary_ddf['date'] = summary_ddf['ts'].dt.date
summary_df = summary_ddf[['date','city', 'position', 'summary']].compute()



# Set Tabs style:
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}



###################
# # Define layout.
###################

#app layout.[

jobs_layout = register_jobs_dashboard_layout(positions, locations, start_date, end_date)
app.layout = jobs_layout


##############
## Callbacks!
##############
register_jobs_dashboard_callbacks(app, jobs_df, companies_df, summary_df)

# CSS styling
external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/xhlulu/0acba79000a3fd1e6f552ed82edb8a64/raw/dash_template.css",
    "https://rawgit.com/plotly/dash-live-model-training/master/custom_styles.css",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

# Launch server.
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
