
###################
# # Define layout.
###################

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

def register_jobs_dashboard_layout(positions, locations, start_date, end_date):
    # tab-1 layout.
    # Banner display
    layout = html.Div(
        children =[
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
                                    multi = True
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
            html.Div(className="container", children=[

                html.Div([ dcc.Graph(id='feature_graphic',
                                    figure = {'data':[
                                                {'x': [1,2], 'y': [3,1]}],
                                    'layout':{'title': ''}})]),
                html.Div([ dcc.Graph(id='feature_graphic2',
                                    figure = {'data':[
                                                {'x': [1,2], 'y': [3,1]}],
                                    'layout':{'title': ''}})])

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
            ])
    ])
    return layout


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
