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
# project import
from jobs_dashboard_callbacks import register_jobs_dashboard_callbacks
from jobs_dashboard_layout import register_jobs_dashboard_layout

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
companies = companies_df.index.get_level_values(1).tolist()
# TODO: to be corrected as now companies_df has city index as ell.
# for city in companies_df.index.get_level_values(0).tolist():
    # for company in companies:
for (city, company) in companies_df.index:
        # df = df.groupby('ts')['cnt'].sum()
    company_traces.append({'x': company, 'y': companies_df.loc[(city, company)], 'name':company})

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
# tab-1 layout.
# Banner display
# tab_1_layout = html.Div(
#     children =[
#         html.Div([
#             html.H2(
#                 'Jobs Dashboard',
#                 id='dashboard_title'
#             ),
#             html.Img(
#                 src="https://i.ibb.co/vZpKhd1/hypercube.jpg"
#             )
#         ],
#             className="banner"
#         ),
#         html.Div(className="row", style={'margin-bottom':'8px'}, children=[
#             html.Div(className="ten columns", children=[
#                 html.Div(
#                     className="four columns",
#                     children=[
#                         html.H6('Position:'),
#                         dcc.Dropdown(
#                             id='position_dropdown',
#                             options = positions,
#                             placeholder='Select a position',
#                             value = ['data scientist', 'data analyst'],
#                             multi = True
#                         )
#                     ]
#                 ),
#
#                 ]
#             )
#             ]
#         ),
#         #Location drop-down component
#         html.Div(
#             className="four columns",
#             children=[
#                 html.H6('Location:'),
#                 dcc.Dropdown(
#                     id='location_dropdown',
#                     options = locations,
#                     placeholder='Select a location',
#                     value = ["Montréal%2C+QC"],
#                     multi = True
#                 )
#             ]
#         ),
#
#         # Date range selection component.
#         html.Div(
#             # html.H4('Select Start and End Date:'),
#             children=[ html.H6('Start and End Date:'),
#                 dcc.DatePickerRange(
#                     id='date_picker_range',
#                     start_date = start_date,
#                     end_date = end_date
#                 )],
#             # style={'width': '30%', 'display': 'block'},
#             className='four columns'
#         ),
#         # Submit button component.
#         html.Div(
#             children = html.Button(
#                 id = 'submit_button',
#                 n_clicks=0,
#                 children='Submit',
#                 # style={'fontSize':24, 'marginLeft':'20px'}
#             ),
#             className='one columns'
#         )
# ])


                # html.Div(
                #     className="four columns",
                #     children=[
                #         html.H6('Location:'),
                #         dcc.Dropdown(
                #             id='location_dropdown',
                #             options = locations,
                #             placeholder='Select a location',
                #             value = ["Montréal%2C+QC"],
                #             multi = True
                #         )
                #     ]
                # ),
#                 html.Div(
#                     # html.H4('Select Start and End Date:'),
#                     children=[ html.H6('Start and End Date:'),
#                         dcc.DatePickerRange(
#                             id='date_picker_range',
#                             start_date = start_date,
#                             end_date = end_date
#                         )],
#                     # style={'width': '30%', 'display': 'block'},
#                     className='four columns'
#                 ),
#                 html.Div(
#                     children = html.Button(
#                         id = 'submit_button',
#                         n_clicks=0,
#                         children='Submit',
#                         # style={'fontSize':24, 'marginLeft':'20px'}
#                     ),
#                     className='one columns'
#                 )
#
#             ]),
#
#             # html.Div(id="div-total-step-count", className="two columns")
#         ]),
#         ],
#         className="container"
#     ),
#     html.Div([ dcc.Graph(id='feature_graphic',
#                         figure = {'data':[
#                                     {'x': [1,2], 'y': [3,1]}],
#                         'layout':{'title': ''}})]),
#     html.Div([ dcc.Graph(id='feature_graphic2',
#                         figure = {'data':[
#                                     {'x': [1,2], 'y': [3,1]}],
#                         'layout':{'title': ''}})]),
#     html.Div([
#         dcc.Graph(
#             id='companies-barchart',
#             figure=go.Figure(
#                 # data = company_traces,
#                 data=[
#                     go.Bar(
#                         x=companies_df.loc["Montréal%2C+QC"].index,
#                         y=companies_df.loc["Montréal%2C+QC"].values[:30],
#                         name='Montréal',
#                         # marker=go.bar.Marker(
#                         #     color='rgb(55, 83, 109)'
#                         # )
#                     ),
#                 ],
#                 layout=go.Layout(
#                     title='top 30 companies by count of jobs postings',
#                     showlegend=True,
#                     # legend=go.layout.Legend(
#                     #     x=0,
#                     #     y=1.0
#                     # ),
#                     # margin=go.Layout.Margin(l=40, r=0, t=40, b=30)
#                 )
#             ),
#             style={'height': 300},
#         )],
#     )
# ]

#app layout.[

jobs_layout = register_jobs_dashboard_layout(positions, locations, start_date, end_date)
app.layout = jobs_layout
#  html.Div([ # ext div.
#     # dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
#     #     dcc.Tab(label='Tab One', value='tab-1-example', style=tab_style, selected_style=tab_selected_style),
#     #     dcc.Tab(label='Tab Two', value='tab-2-example', style=tab_style, selected_style=tab_selected_style),
#     # ],
#     # style=tabs_styles),
#     # html.Div(id='tabs-content-example'),
#     tab_1_layout
# ], style={'padding':10})


##############
## Callbacks!
##############
register_jobs_dashboard_callbacks(app, jobs_df, companies_df)

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
    app.run_server(host='0.0.0.0', debug=True)
