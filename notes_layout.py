
###################
# # Define layout.
###################

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly as py

def register_notes_layout():

    # tab-1 layout.
    # Banner display
    layout = html.Div(
        children =[
            html.Div([
                html.Nav(className = "nav nav-pills", children=[
                    html.A('Dashboard', className="nav-item nav-link btn", href='/job_seeker'),
                    # html.A('Report', className="nav-item nav-link btn", href='/apps/App2'),
                    html.A('Dask', className="nav-item nav-link btn", href='/dask'),
                    # html.A('RAPIDS', className="nav-item nav-link btn", href='/rapids'),
                    html.A('Notes', className="nav-item active nav-link btn", href='/notes'),
                    html.A('Useful Links', className="nav-item nav-link btn", href='/links'),
                    ]),
                ]),
                html.Div(
                      [
                        dcc.Markdown(
                            '''
                            ### Some Notes about this multipages Plotly Dash app.

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
