# Code along project
###################

# Imports.
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
# import pandas_datareader.data as web
import pandas as pd
from sqlalchemy import create_engine
from dask import delayed as delay
import ipdb

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
# Define app.
app = dash.Dash()

# Load Data.
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
# ipdb.set_trace()
# # Define layout.
app.layout = html.Div([ # ext div.
    html.H1('Jobs Dashboard', id='dashboard_title'),
    html.Div([
        html.H4('Select position:'),
        dcc.Dropdown(
            id='symbol_dropdown',
            options = positions,
                # [
                # {'label': 'AAPL', 'value': 'AAPL'}
                # ], # We'll need to modify this with companies symbol in df.
                value = ['data scientist', 'data analyst'],
                multi = True)],
        style={'width': '30%', 'display': 'inline-block', 'verticalAlign':'top'}),
    html.Div([
        html.H4('Select location:'),
        dcc.Dropdown(
            id='location_dropdown',
            options = locations,
                value = ["Montréal%2C+QC"],
                multi = True)],
        style={'width': '30%', 'display': 'inline-block', 'verticalAlign':'top'}),
    html.Div([
        html.H4('Select Start and End Date:'),
        dcc.DatePickerRange(
            id='date_picker_range',
            start_date = start_date,
            end_date = end_date
        )
    ],
        style={'width': '30%', 'display': 'inline-block'}),
    html.Button(
        id = 'submit_button',
        n_clicks=0,
        children='Submit',
        style={'fontSize':24, 'marginLeft':'30px'}
    ),
    html.Div([ dcc.Graph(id='feature_graphic',
                        figure = {'data':[
                                    {'x': [1,2], 'y': [3,1]}],
                        'layout':{'title': ''}})])
], style={'padding':10})
#
# # Callbacks:
@app.callback(
    Output('feature_graphic', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('symbol_dropdown', 'value'),
     State('location_dropdown', 'value'),
     State('date_picker_range' ,'start_date'),
     State('date_picker_range' ,'end_date')],
    )
def update_graph(n_clicks, symbols, locations, start_date, end_date):
    traces = []
    for symb in symbols:
        for location in locations:
            # TODO: to be modified. use index for ts in order to have daily count?
            # df = web.DataReader(symb, 'iex', start_date, end_date)
            df = jobs_df[ (jobs_df['position'] == symb) & (jobs_df['city'] == location)]
            df = df.groupby('ts')['cnt'].sum()
            print(df.head())
            # df['ts'] = pd.to_datetime(df['ts']
            # df.set_index('ts')
            traces.append({'x': df.index, 'y': df.values, 'name': symb + ' - ' + location})
    fig = { 'data':traces,
            'layout':{'title': symbols}
        }
    return fig

# Launch server.
if __name__ == '__main__':
    app.run_server()
