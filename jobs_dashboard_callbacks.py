
#########################
# Jobs dashboard callbacks
#########################
from dash.dependencies import Input, Output, State
import plotly.offline as pyo
import plotly.graph_objs as go
import ipdb

# Compute words frequencies in jobs postings.
# nlp imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import plotly as py
import random

from dask import delayed as delay
from datetime import datetime as dt
import pandas as pd
from sqlalchemy import create_engine

################
# # Callbacks:
################
# Callback for tabs:
# TODO: put each tab in separate files.

def register_jobs_dashboard_callbacks(app, jobs_df, companies_df, summary_ddf):

    @app.callback(
        Output('feature_graphic', 'figure'),
        [Input('submit_button', 'n_clicks')],
        [State('position_dropdown', 'value'),
         State('location_dropdown', 'value'),
         State('date_picker_range' ,'start_date'),
         State('date_picker_range' ,'end_date')],
        )
    def update_graph(n_clicks, positions, locations, start_date, end_date):
        traces = []
        for position in positions:
            for location in locations:
                # TODO: to be modified. use index for ts in order to have daily count?
                # df = web.DataReader(symb, 'iex', start_date, end_date)
                df = jobs_df[ (jobs_df['position'] == position) & (jobs_df['city'] == location)]
                df = df.groupby('ts')['cnt'].sum()
                traces.append({'x': df.index, 'y': df.values, 'name': position + ' - ' + location.split('%')[0]})
        fig = { 'data':traces,
                'layout':{
                'title': positions,
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
            df = jobs_df[ (jobs_df['position'] == 'data analyst') & (jobs_df['city'] == location)]
            df_total_location = jobs_df[ (jobs_df['city'] == location)]
            df = df.groupby('ts')['cnt'].sum() # Count for data analyst positions
            df_total_location = df_total_location.groupby('ts')['cnt'].sum()
            print(df)
            print(df_total_location)
            df_ratio = df / df_total_location
            df_ratio = df_ratio.interpolate()
            print(df_ratio.head())
            df_complement = 1 - df_ratio

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
    def update_barchart(n_clicks, positions, locations, start_date, end_date):
        company_traces = []
        # This part works to top30 for locations mixed.
        # TODO: add position
        companies_locations = companies_df.loc[locations]
        # Adding position selection.
        # companies_locations = companies_locations[companies_locations['position'].isin(positions)]
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


    # update words cloud chart graph for most common words in jobs postings.

    @app.callback(
        Output('words-cloud', 'figure'),
        [Input('submit_button', 'n_clicks')],
        [State('position_dropdown', 'value'),
         State('location_dropdown', 'value'),
         State('date_picker_range' ,'start_date'),
         State('date_picker_range' ,'end_date')],
        )
    def update_words_cloud(n_clicks, positions, locations, start_date, end_date):
        # from summary_df, we shoul compute the most common words
        # summary_df.columns = ['date', 'city', 'position', 'summary']

        # Taking a sample to test program.
        summary_df = summary_ddf.set_index('date').sort_index()
        print('start: '  + str(type(start_date)))
        print(start_date)
        print(summary_df.head())
        # select data from filters selections.
        summary_df = summary_df.loc[pd.to_datetime(start_date).date() : pd.to_datetime(end_date).date()]
        filters_select = (summary_df['city'].isin(locations)) & (summary_df['position'].isin(positions))
        summary_df = summary_df[filters_select]

        summary_df = summary_df['summary']
        summary_df = summary_df.drop_duplicates()
        all_words =[]
        for description in summary_df:
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

        # set colors and format.
        lenth = len(words)
        colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(lenth)]

        figure=go.Figure(
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

        )
        return figure
