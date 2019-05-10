import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table

# df = pd.read_csv(
#     'https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/'
    'c78bf172206ce24f77d6363a2d754b59/raw/'
    'c353e8ef842413cae56ae3920b8fd78468aa4cb2/'
    'usa-agricultural-exports-2011.csv')


# def generate_table(dataframe, max_rows=10):
#     return html.Table(
#         # Header
#         [html.Tr([html.Th(col) for col in dataframe.columns])] +
#
#         # Body
#         [html.Tr([
#             html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#         ]) for i in range(min(len(dataframe), max_rows))]
#     )
def generate_table(dataframe, max_rows=10, _id='table'):
    return dash_table.DataTable(
        id=_id,
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
        n_fixed_rows=1,
        style_table={
            'overflowX': 'scroll',
            'maxHeight': '1000px',
            'overflowY': 'scroll',
            'border': 'thin lightgrey solid'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'state'},
             'width': '10%'}
        ]
    )


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# app.layout = html.Div(children=[
#     html.H4(children='US Agriculture Exports (2011)'),
#     html.Div([
#         html.Div([
#             generate_table(df),
#         ], className='six columns'),
#         html.Div([
#             generate_table(df, _id='table2'),
#         ], className='six columns')
#     ])
# ])

app.layout = html.Div(children=[
    html.H4(children='US Agriculture Exports (2011)'),
    html.Div([
        html.Div([
            generate_table(df),
        ], className='nine columns'),
        html.Div(className='three columns')
    ], className='twelve columns'),
    # html.Div(className='three columns'),
    html.Br(),
    # html.Div([
    #     html.Div('Example Div', style={'color': 'blue', 'fontSize': 14}),
    #     html.P('Example P', className='my-class', id='my-p-element')
    # ], style={'marginBottom': 50, 'marginTop': 25})
    html.H4('testtest')
])


if __name__ == '__main__':
    app.run_server(debug=True)