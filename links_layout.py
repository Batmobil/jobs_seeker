
###################
# # Define layout.
###################

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly as py

def register_links_layout():

    # tab-1 layout.
    # Banner display
    layout = html.Div(
        children =[
            html.Div([
                html.Nav(className = "nav nav-pills", children=[
                    html.A('Dashboard', className="nav-item nav-link btn", href='/job_seeker'),
                    html.A('Report', className="nav-item nav-link btn", href='/apps/App2'),
                    html.A('Dask', className="nav-item nav-link btn", href='/dask'),
                    html.A('Notes', className="nav-item nav-link btn", href='/notes'),
                    html.A('Useful Links', className="nav-item active nav-link btn", href='/links'),
                    ]),
                ]),
                html.Div(
                      [
                        dcc.Markdown(
                            '''
                            ### Some Notes about this multipages Plotly Dash app.

                            Here are some useful links that helped me setting up this app:
                                - The plotly dash library and [documentation](https://dash.plot.ly/).
                                - The excellent detailed [article](https://towardsdatascience.com/how-to-build-a-complex-reporting-dashboard-using-dash-and-plotl-4f4257c18a7f) on multipage Dash app from David Comfort (setting all of these in two weeks from scratch, nice job!).
                                - Dask [library](https://docs.dask.org/en/latest/).
                                - The very enlightning [article](https://medium.com/when-i-work-data/processing-data-with-dask-47e4233cf165) on data processing with Dask by Eric Ness.


                            ### Here are some useful snippets for the use of dask, a library that deserves better recognition.
                            ```python
                            #Loading Word clouds data.
                            query_jobs_data = """SELECT * FROM indeed WHERE ts >= %(start)s AND ts < %(end)s """
                            rds_connection = ####connection_string####
                            summary_ddf = ddf.read_sql_table(####table_name####, rds_connection, index_col='ts')
                            summary_ddf = summary_ddf[['city', 'position', 'summary']].reset_index()
                            summary_ddf['date'] = summary_ddf['ts'].dt.date
                            summary_df = summary_ddf[['date','city', 'position', 'summary']].compute()
                            ```

                            '''.replace('  ', '')
                            ,
                            className='eight columns offset-by-two'
                        )
                      ],
                      className='row',
                      style={'text-align': 'left', 'margin-bottom': '15px'}
                  )
    ])
    return layout
