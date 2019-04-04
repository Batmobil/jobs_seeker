
###################
# # Define layout.
###################

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly as py

# Compute words frequencies in jobs postings.
# nlp imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from dask import delayed as delay
from datetime import datetime as dt
import pandas as pd
from sqlalchemy import create_engine
import random

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
    all_words.extend(words)

text = nltk.Text(all_words)
# Calculate Frequency distribution
freq = nltk.FreqDist(text)

# Print and plot most common words
words_count = freq.most_common(30)

words = [count[0] for count in words_count]
frequency = [count[1] for count in words_count]
percent = [frequ / sum(frequency) for frequ in frequency]

lower, upper = 15, 45
frequency = [((x - min(frequency)) / (max(frequency) - min(frequency))) * (upper - lower) + lower for x in frequency]

lenth = len(words)
colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(lenth)]

def register_jobs_dashboard_layout(positions, locations, start_date, end_date):


    # tab-1 layout.
    # Banner display
    layout = html.Div(
        children =[
            html.Div([
                html.Nav(className = "nav nav-pills", children=[
                    html.A('Dashboard', className="nav-item active nav-link btn", href='/job_seeker'),
                    html.A('Report', className="nav-item nav-link btn", href='/apps/App2'),
                    html.A('Dask', className="nav-item nav-link btn", href='/dask'),
                    html.A('Notes', className="nav-item nav-link btn", href='/notes'),
                    html.A('Useful Links', className="nav-item nav-link btn", href='/links'),
                    ]),
                ]),
            html.Div([
                html.H2(
                    'Jobs Dashboard',
                    id='dashboard_title'
                ),
                html.Img(
                    src="https://i.ibb.co/vZpKhd1/hypercube.jpg"
                )
            ],
                className="banner"
            ),
            html.Div(className="container", children=[

                html.Div(
                      [
                        dcc.Markdown(
                            '''
                            ### Project description:
                            Looking for a job as a data analyst or data scientist, I wanted to get a better idea of the job market
                            for these two positions in Montreal, Qc.
                            So I gathered few pieces together in order to get a functionnal dashboard of number of jobs postings for both positions in Montreal.
                            * I used a web scraper script (scrape_jobs.py) to fetch various jobs posting info and do basic processing data
                            from a very popular jobs aggregator website and store these info into a MySQL database on AWS (RDS).
                            For now, this script has to be run manually every day but we could automatate the daily scraping with a basic cronjob on a remote server/instance.

                            * On the visualisation side, I used the excellent Dash library from Plotly as an open source tool to visualize data.
                            As the Dash app is based on Flask, some knowledge about flask framework were required.

                            To display data, some procession is done between the database query and the various visualisations, pandas, dask, and nltk (word cloud) packages were of great help.
                            The use of nltk make the dashboard a bit slow to load at start as Dash do all the data processing and load necessary data for the dashboard in memory.
                            The dashboard is not refreshed automatically with new daily data as this is one limitation from plotly similarly as Tableau or other BI tools, Dash does not allow
                            data streaming out of the box, but the use of Redis or other strategies could allow to achieve this result if necessary.

                            Some future improvements at various levels can be done:
                            * Port the mutipage dash app to a more classic flask app, allowing web development of other pages easily while keeping the dashboards.
                            * Adding some other visualisations to the jobs dashboard, like gauge for variations fro week to week for instance.
                            * Improve the word cloud display, both on processing, while I wanted to be able to make the filter work on the word cloud, this make the app very slow to load
                            as some data (basic nlp woth nltk) processing is happening behind the scene. Also a decicated wrod cloud dash component can be improved with a react component that has yet to be develop by the Dash community.

                            The code for this project is available on github [here](https://github.com/Batmobil/jobs_seeker).

                            '''.replace('  ', '')
                            ,
                            className='ten columns'
                        )
                      ],
                      className='row',
                      style={'text-align': 'left', 'margin-bottom': '15px'}
                  ),

                html.Div(className="row", style={'margin-bottom':'8px'}, children=[
                    html.Div(className="ten columns", children=[
                        html.Div(
                            className="four columns",
                            children=[
                                html.H6('Position:'),
                                dcc.Dropdown(
                                    id='position_dropdown',
                                    options = positions,
                                    placeholder='Select a position',
                                    value = ['data scientist', 'data analyst'],
                                    multi = The code for this project is available on github [here](https://github.com/Batmobil/jobs_seeker).True
                                )
                            ]
                        ),

                        #Location drop-down component
                        html.Div(
                            className="four columns",
                            children=[
                                html.H6('Location:'),
                                dcc.Dropdown(
                                    id='location_dropdown',
                                    options = locations,
                                    placeholder='Select a location',
                                    value = ["Montréal%2C+QC"],
                                    multi = True
                                )
                            ]
                        ),
                        # Date range selection component.
                        html.Div(
                            # html.H4('Select Start and End Date:'),
                            children=[ html.H6('Start and End Date:'),
                                dcc.DatePickerRange(
                                    id='date_picker_range',
                                    start_date = start_date,
                                    end_date = end_date
                                )],
                            # style={'width': '30%', 'display': 'block', 'height': 2},
                            className='four columns'
                        ),
                        # Submit button component.
                        html.Div(
                            children = html.Button(
                                id = 'submit_button',
                                n_clicks=0,
                                children='Submit',
                                # style={'fontSize':24, 'marginLeft':'20px'}
                            ),
                            className='one columns'
                        ),

                    ])
                    ]
                ),

            ]),

            # Words cloud
            html.Div(className='container',children=[
                html.Div(className = 'twelve columns', children=[
                dcc.Graph(
                    id='words-cloud',
                    figure=go.Figure(
                        # data = company_traces,

                        data = [
                            go.Scatter(
                                x=list(range(lenth)),
                                y=random.choices(range(lenth), k=lenth),
                                mode='text',
                                text=words,
                                hovertext=['{0}{1}{2}'.format(w, f, format(p, '.2%')) for w, f, p in zip(words, frequency, percent)],
                                hoverinfo='text',
                                textfont={'size': frequency, 'color': colors}
                                )
                            ],
                        layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                                                'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

                    ),
                    style={'height': 300},
                )
            ])]),
            html.Div(className="container", children=[
                html.Div(className= 'six columns', children=[
                    html.Div([ dcc.Graph(id='feature_graphic',
                                        figure = {'data':[
                                                    {'x': [1,2], 'y': [3,1]}],
                                        'layout':{'title': ''}})]),
                            html.Div([ dcc.Graph(id='feature_graphic2',
                                    figure = {'data':[
                                                {'x': [1,2], 'y': [3,1]}],
                                    'layout':{'title': ''}})])
                ])
            ]),
            html.Div(className='container',children=[
                dcc.Graph(
                    id='companies-barchart',
                    figure=go.Figure(
                        # data = company_traces,
                        data=[
                            go.Bar(
                                x =[1,2],
                                y=[3,1],
                                # x=companies_df.loc["Montréal%2C+QC"].index,
                                # y=companies_df.loc["Montréal%2C+QC"].values[:30],
                                name='Montréal',
                                # marker=go.bar.Marker(
                                #     color='rgb(55, 83, 109)'
                                # )
                            ),
                        ],
                        layout=go.Layout(
                            title='top 30 companies by count of jobs postings',
                            showlegend=True,
                            # legend=go.layout.Legend(
                            #     x=0,
                            #     y=1.0
                            # ),
                            # margin=go.Layout.Margin(l=40, r=0, t=40, b=30)
                        )
                    ),
                    style={'height': 300},
                )
            ]),


    ])
    return layout
