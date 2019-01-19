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
# Define app and authentication.
USERNAME_PASSWORD_PAIRS = [['baptiste', 'baptiste86']]
app = dash.Dash()
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

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

# count by company:
company_traces = []
companies_df = jobs_df.groupby(['city', 'company_name'])['cnt'].sum().sort_values(ascending=False)
companies = companies_df.index
for company in companies:
    # df = df.groupby('ts')['cnt'].sum()
    company_traces.append({'x': company, 'y': companies_df.loc[company], 'name':company})

# ipdb.set_trace()
# # Define layout.
app.layout = html.Div([ # ext div.
    # Banner display
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
    # html.Div([
    #     html.H1(
    #         'Jobs Dashboard',
    #         id='dashboard_title'
    #     )
    # ],
    #     className="banner"
    # ),

     # dcc.Tabs(
     #            id="tabs",
     #            style={"height":"20","verticalAlign":"middle"},
     #            children=[
     #                dcc.Tab(label="Count", value="opportunities_tab"),
     #                dcc.Tab(label="Leads", value="leads_tab"),
     #                dcc.Tab(id="cases_tab",label="Cases", value="cases_tab"),
     #            ],
     #            value="leads_tab",
     #        ),
    html.Div([
        html.Div(className="row", style={'margin-bottom':'8px'}, children=[
            html.Div(className="ten columns", children=[
                html.Div(
                    className="four columns",
                    children=[
                        html.H6('Position:'),
                        dcc.Dropdown(
                            id='symbol_dropdown',
                            options = positions,
                            placeholder='Select a position',
                            value = ['data scientist', 'data analyst'],
                            multi = True
                        )
                    ]
                ),

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
                html.Div(
                    # html.H4('Select Start and End Date:'),
                    children=[ html.H6('Start and End Date:'),
                        dcc.DatePickerRange(
                            id='date_picker_range',
                            start_date = start_date,
                            end_date = end_date
                        )],
                    # style={'width': '30%', 'display': 'block'},
                    className='four columns'
                ),
                html.Div(
                    children = html.Button(
                        id = 'submit_button',
                        n_clicks=0,
                        children='Submit',
                        # style={'fontSize':24, 'marginLeft':'20px'}
                    ),
                    className='one columns'
                )

            ]),

            # html.Div(id="div-total-step-count", className="two columns")
        ]),
        ],
        className="container"
    ),

    # html.Div([
    #     html.H4('Select position:'),
    #     dcc.Dropdown(
    #         id='symbol_dropdown',
    #         options = positions,
    #             value = ['data scientist', 'data analyst'],
    #             multi = True)],
    #     style={'width': '20%', 'height': 10, 'display': 'block', 'verticalAlign':'top'}),
    # html.Div([
    #     html.H4('Select location:'),
    #     dcc.Dropdown(
    #         id='location_dropdown',
    #         options = locations,
    #             value = ["Montréal%2C+QC"],
    #             multi = True)],
    #     style={'width': '20%', 'display': 'block', 'verticalAlign':'top'}),
    # html.Div([
    #     html.H4('Select Start and End Date:'),
    #     dcc.DatePickerRange(
    #         id='date_picker_range',
    #         start_date = start_date,
    #         end_date = end_date
    #     )
    # ],
    #     style={'width': '30%', 'display': 'block'}
    # ),
    # html.Button(
    #     id = 'submit_button',
    #     n_clicks=0,
    #     children='Submit',
    #     style={'fontSize':24, 'marginLeft':'20px'}
    # ),
    html.Div([ dcc.Graph(id='feature_graphic',
                        figure = {'data':[
                                    {'x': [1,2], 'y': [3,1]}],
                        'layout':{'title': ''}})]),
    html.Div([ dcc.Graph(id='feature_graphic2',
                        figure = {'data':[
                                    {'x': [1,2], 'y': [3,1]}],
                        'layout':{'title': ''}})]),
    html.Div([ dcc.Graph(
    figure=go.Figure(
        # data = company_traces,
        data=[
            go.Bar(
                x=companies,
                y=companies_df.values,
                # name='Rest of world',
                # marker=go.bar.Marker(
                #     color='rgb(55, 83, 109)'
                # )
            ),
        ],
        layout=go.Layout(
            title='# of jobs postings by company',
            showlegend=True,
            # legend=go.layout.Legend(
            #     x=0,
            #     y=1.0
            # ),
            # margin=go.Layout.Margin(l=40, r=0, t=40, b=30)
        )
    ),
    style={'height': 300},
    id='companies-barchart'
)])



], style={'padding':10})
################
# # Callbacks:
################
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
            traces.append({'x': df.index, 'y': df.values, 'name': symb + ' - ' + location.split('%')[0]})
    fig = { 'data':traces,
            'layout':{
            'title': symbols,
            'autosize':True,
            'yaxis':{
                'title':"# of jobs"
                }
            }
        }
    return fig

# update 2nd graph for % jobs

@app.callback(
    Output('feature_graphic2', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('symbol_dropdown', 'value'),
     State('location_dropdown', 'value'),
     State('date_picker_range' ,'start_date'),
     State('date_picker_range' ,'end_date')],
    )
def update_graph2(n_clicks, symbols, locations, start_date, end_date):
    traces = []
    for symb in symbols:
        for location in locations:
            # TODO: to be modified. use index for ts in order to have daily count?
            # df = web.DataReader(symb, 'iex', start_date, end_date)
            df = jobs_df[ (jobs_df['position'] == symb) & (jobs_df['city'] == location)]
            df_total_location = jobs_df[ (jobs_df['city'] == location)]
            df = df.groupby('ts')['cnt'].sum()
            df_total_location = df_total_location.groupby('ts')['cnt'].sum()
            print(df)
            print(df_total_location)
            df_ratio = df / df_total_location
            print(df_ratio.head())
            # df_ratio = df_ratio.groupby('ts').sum()

            traces.append({'x': df.index, 'y': 100 * df_ratio.values, 'name': symb + ' - ' + location.split('%')[0]})
    fig = { 'data':traces,
            'layout':{
            'title': symbols,
            'autosize':True,
            'yaxis':{
                'title':"% of positions among DA and DS"
                }
            }
        }
    return fig

# # update Bar chart graph for jobs postings by companies.

@app.callback(
    Output('companies-barchart', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('symbol_dropdown', 'value'),
     State('location_dropdown', 'value'),
     State('date_picker_range' ,'start_date'),
     State('date_picker_range' ,'end_date')],
    )
def update_barchart(n_clicks, symbols, locations, start_date, end_date):
    company_traces = []
    for location in locations:
        comp_city = companies_df.loc[location].head(30)
        print(comp_city.head())
        company_traces.append(go.Bar(
                                x=comp_city.index,
                                y=companies_df.values,
                                name=location,
                                    )
                            )
    fig = { 'data':company_traces,
            'layout':{
            'title': 'Top 30 companies by count of jobs postings',
            'showlegend':True,
            'autosize':True,
            'yaxis':{
                'title':"# of jobs postings"
                }
            }
        }
    return fig

# CSS styling
external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/xhlulu/0acba79000a3fd1e6f552ed82edb8a64/raw/dash_template.css",
    "https://rawgit.com/plotly/dash-live-model-training/master/custom_styles.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

# Launch server.
if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
