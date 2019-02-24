
#########################
# Jobs dashboard callbacks
#########################
from dash.dependencies import Input, Output, State
import plotly.offline as pyo
import plotly.graph_objs as go

################
# # Callbacks:
################
# Callback for tabs:
# TODO: put each tab in separate files.

def register_jobs_dashboard_callbacks(app, jobs_df, companies_df):
    # @app.callback(Output('tabs-content-example', 'children'),
    #               [Input('tabs-example', 'value')])
    # def render_content(tab):
    #     if tab == 'tab-1-example':
    #         return tab_1_layout
    #     elif tab == 'tab-2-example':
    #         return html.Div([
    #             html.H3('Tab content 2'),
    #             dcc.Graph(
    #                 id='graph-2-tabs',
    #                 figure={
    #                     'data': [{
    #                         'x': [1, 2, 3],
    #                         'y': [5, 10, 6],
    #                         'type': 'bar'
    #                     }]
    #                 }
    #             )
    #         ])
    #

    @app.callback(
        Output('feature_graphic', 'figure'),
        [Input('submit_button', 'n_clicks')],
        [State('position_dropdown', 'value'),
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
        [State('position_dropdown', 'value'),
         State('location_dropdown', 'value'),
         State('date_picker_range' ,'start_date'),
         State('date_picker_range' ,'end_date')],
        )
    def update_graph2(n_clicks, positions, locations, start_date, end_date):
        traces = []
        # We only compute ratio from DA position numbers as we have less timestamps for this position.
        # for position in positions:
        for location in locations:
            # TODO: to be modified. use index for ts in order to have daily count?
            # df = web.DataReader(symb, 'iex', start_date, end_date)
            df = jobs_df[ (jobs_df['position'] == 'data analyst') & (jobs_df['city'] == location)]
            df_total_location = jobs_df[ (jobs_df['city'] == location)]
            df = df.groupby('ts')['cnt'].sum()
            # df = df.resample('D').ffill()
            # df = df.rolling(4).mean()
            df_total_location = df_total_location.groupby('ts')['cnt'].sum()
            # df_total_location = df_total_location.resample('D').ffill()
            # df_total_location = df_total_location.rolling(4).mean()
            print(df)
            print(df_total_location)
            df_ratio = df / df_total_location
            print(df_ratio.head())
            df_complement = 1 - df_ratio
            # df_ratio = df_ratio.groupby('ts').sum()

            traces.append({'x': df_ratio.index,
                           'y': 100 * df_ratio.values,
                           'name': 'data analyst' + ' - ' + location.split('%')[0],
                           'mode': 'lines',
                           'stackgroup': 'one' })
            traces.append({'x': df_complement.index,
                           'y': 100 * df_complement.values,
                           'name': 'data scientist' + ' - ' + location.split('%')[0],
                           'mode': 'lines',
                           'stackgroup': 'one'})
        fig = { 'data':traces,
                'layout':{
                'title': positions,
                'autosize':True,
                'yaxis':{
                    'title':"% of positions among DA and DS",
                    'type': 'linear',
                    'range': [1, 100],
                    'ticksuffix': '%'
                    }
                }
            }
        return fig

    # # update Bar chart graph for jobs postings by companies.

    @app.callback(
        Output('companies-barchart', 'figure'),
        [Input('submit_button', 'n_clicks')],
        [State('position_dropdown', 'value'),
         State('location_dropdown', 'value'),
         State('date_picker_range' ,'start_date'),
         State('date_picker_range' ,'end_date')],
        )
    def update_barchart(n_clicks, symbols, locations, start_date, end_date):
        company_traces = []
        # This part works to top30 for locations mixed.
        companies_locations = companies_df.loc[locations]
        top30 = companies_locations.head(30)
        top30 = top30.reset_index()
        # for location in locations:
            # comp_city = companies_df.loc[location].head(30)
        print('top30')
        print(top30)
        # for rank in top30['company_name'].index.tolist():
        company_traces.append(go.Bar(
                                x=top30['company_name'],
                                # x=top30['company_name'],
                                y=top30['cnt'],
                                # name=top30.loc[rank, 'city'],
                                    )
                            )
        fig = { 'data':company_traces,
                'layout':{
                'title': 'Top 30 companies by count of jobs postings',
                'showlegend':False,
                'autosize':True,
                'yaxis':{
                    'title':"count of jobs postings"
                    }
                }
            }

        print(fig)
        return fig
        # TODO: correct x-axis issue
        # for location in locations:
        #     top30 = companies_df.loc[locations].head(30).reset_index()
        #     company_traces.append(go.Bar(
        #                             x=top30['company_name'],
        #                             y=top30['cnt'],
        #                             name=location.rstrip(r'%')
        #                             )
        #                         )
        #
        # fig = { 'data':company_traces,
        #         'layout':
        #             {
        #             'title': 'Top 30 companies by count of jobs postings',
        #             'showlegend':True,
        #             'autosize':True,
        #             'yaxis':{
        #                 'title':"count of jobs postings"
        #                 },
        #             # 'barmode': 'group'
        #             }
        #     }
        # print(fig)
        # return fig
