import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, db, HistoricalPrice, Ticker, Users, Portfolio
import dash_table
import pandas as pd
import sqlalchemy
import fix_yahoo_finance as yf
import plotly.graph_objs as go
from sqlalchemy import exc


def fetch_data(q, session):
    result = pd.read_sql(
        sql=q,
        con=session
    )
    return result


def fecth_stock_info(strTickerlist):
    strList = strTickerlist.split()
    # df_temp = pd.DataFrame(columns=['TickerID', 'TickerShortName', 'TickerType'])
    # strList = strList.split()
    rows_list = []
    result = db.session.query(Ticker.TickerID).group_by(Ticker.TickerID).all()
    dbTickerList =[]
    if result is not None and len(result) > 0:
        dbTickerList = [temp[0] for temp in result]
    for ticker in strList:
        tempdict = {}
        if ticker in dbTickerList:
            continue
        tempdict['TickerID'] = ticker
        tempdict['TickerShortName'] = yf.Ticker(ticker).info['shortName']
        tempdict['TickerType'] = yf.Ticker(ticker).info['quoteType']
        rows_list.append(tempdict)
    df_temp = pd.DataFrame(rows_list)
    df_temp.to_sql(name="Ticker", con=db.session.bind, if_exists='append', index=False,
                   dtype={'TickerID': sqlalchemy.types.VARCHAR(length=20),
                          'TickerShortName':  sqlalchemy.types.VARCHAR(length=80),
                          'TickerType': sqlalchemy.types.VARCHAR(length=20)})


def fetch_all_stocks(strTickerlist, start, end):
    symbols = strTickerlist.split()

    # start = "2013-01-01"
    # end = "2018-12-01"

    # Here is our query.
    # data = pdr.get_data_yahoo(symbols, start="2015-01-01", end="2018-12-01")
    data = yf.download(
        tickers=symbols,
        start=start,
        end=end,
        group_by='ticker'
    )
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Ticker'
                               ])
    for c in symbols:
        df_temp = data[c].reset_index()
        df_temp['Ticker'] = c
        df = df.append(df_temp)

    df_export = df.rename(columns={'Date': '_Date',
                                   'Adj Close': 'Adj_Close',
                                   'Close': 'ClosingPrice',
                                   'Ticker': 'TickerID'})[['TickerID', '_Date', 'ClosingPrice', 'Adj_Close', 'Volume']]

    db.session.query(HistoricalPrice).delete()
    db.session.commit()

    df_export.to_sql(name="HistoricalPrice", con=db.session.bind, if_exists='append', index=False,
                     dtype={'Ticker': sqlalchemy.types.VARCHAR(length=20),
                            '_Date': sqlalchemy.types.DateTime(),
                            'ClosingPrice': sqlalchemy.types.Float(asdecimal=True),
                            'Adj_Close': sqlalchemy.types.Float(asdecimal=True),
                            'Volume': sqlalchemy.types.BIGINT})


def fetch_users():
    user_query = (
        f'''
        SELECT *
        FROM Users
        '''
    )
    conn = db.session.bind
    table = fetch_data(user_query, conn)

    return dash_table.DataTable(
        id='table-users',
        columns=[{"name": i, "id": i} for i in table.columns],
        data=table.to_dict('records'),
        n_fixed_rows=1
    )


def fetch_users_options():
    userlist = db.session.query(Users.UserID).all()
    if len(userlist) > 0:
        optionList =[]
        for temp in userlist:
            optionList.append({'label': temp[0], 'value': temp[0]})
        return optionList
    else:
        return []



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


def serve_layout():
    # tickerlist = db.session.query(HistoricalPrice.TickerID).group_by(HistoricalPrice.TickerID).all()
    obj_usertable = fetch_users()
    user_optionList = fetch_users_options()
    admin_layout = html.Div([
        html.Div(id='signal-1', style={'display': 'none'}),
        html.Div(id='signal-2', style={'display': 'none'}),
        html.Div(id='signal-3', style={'display': 'none'}),
        dcc.Tabs(id='admin-tabs', children=[
            dcc.Tab(id='admin-user-tab', label='User Management', children=[
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5('Add user:'),
                            html.Label('UserID', htmlFor='input-UserId'),
                            dcc.Input(
                                placeholder='User name, e.g. wmu100',
                                type='text',
                                value='',
                                id='input-UserId'
                            ),
                            html.Label('Password', htmlFor='input-UserPassword'),
                            dcc.Input(
                                placeholder='e.g. abcde@syr.edu',
                                type='password',
                                value='',
                                id='input-UserPassword'
                            ),
                            html.Label('User type', htmlFor='input-UserType'),
                            dcc.Input(
                                placeholder='either student or admin',
                                type='text',
                                value='',
                                id='input-UserType'
                            ),
                            html.Label('First name', htmlFor='input-UserFN'),
                            dcc.Input(
                                placeholder='e.g. Wei',
                                type='text',
                                value='',
                                id='input-UserFN'
                            ),
                            html.Label('Last name', htmlFor='input-UserLN'),
                            dcc.Input(
                                placeholder='e.g. Dahai',
                                type='text',
                                value='',
                                id='input-UserLN'
                            ),
                            # html.Button('Add', id='adduser-button', n_clicks=0, className='button-primary'),
                            html.Button('Add', id='adduser-button', n_clicks=0, className='button-primary',
                                        style={'margin-left': '10px'}),
                            html.Br(),
                            html.Br(),
                            html.P(html.A('Go to general user (student) page', href='/apps/main'))
                        ], className='six columns'),
                        html.Div([
                            # Modify
                            #
                            html.H5('Modify or drop user:'),
                            html.Label('UserID', htmlFor='user-dropdown'),
                            html.Div([
                                dcc.Dropdown(
                                    id='user-dropdown',
                                    options=user_optionList,
                                    value='',
                                    className='three columns'
                                ),
                            ], className='twelve columns'),
                            html.Label('Password', htmlFor='input2-UserPassword'),
                            dcc.Input(
                                placeholder='e.g. abcde@syr.edu',
                                type='password',
                                value='',
                                id='input2-UserPassword'
                            ),
                            html.Label('User type', htmlFor='input2-UserType'),
                            dcc.Input(
                                placeholder='either student or admin',
                                type='text',
                                value='',
                                id='input2-UserType'
                            ),
                            html.Label('First name', htmlFor='input2-UserFN'),
                            dcc.Input(
                                placeholder='e.g. Wei',
                                type='text',
                                value='',
                                id='input2-UserFN'
                            ),
                            html.Label('Last name', htmlFor='input2-UserLN'),
                            dcc.Input(
                                placeholder='e.g. Dahai',
                                type='text',
                                value='',
                                id='input2-UserLN'
                            ),
                            html.Button('Modify', id='modifyuser-button', n_clicks=0, className='button-primary',
                                        style={'margin-left': '10px'}),
                            html.Button('DROP', id='deluser-button', n_clicks=0, className='button-primary',
                                        style={'margin-left': '10px', 'background-color':'#fa4f56'})
                        ], className='six columns')
                    ], className='six columns'),
                    html.Div([
                        html.H5('All users in the system:'),
                        html.Span([
                            obj_usertable
                        ], id='user-data-area'),
                        html.H5('Number of users accounts in the system:'),
                        html.P(id='num-of-users'),
                    ], className='six columns')
                ], className='twelve columns')
            ], style=tab_style, selected_style=tab_selected_style),

            dcc.Tab(id='admin-finance-tab', label='Financial Data',  children=[
                html.Div([
                    html.H4('Refresh historical data'),
                    html.P('Please input stock tickers, separated by spaces, e.g. \'AAPL MSFT \''),
                    html.P('Please do not input apostrophes, commas, or any other special characters'),
                    html.P('When Refresh is clicked, all historical price data not included in the date range '
                           'below will be removed.'),
                    html.P('The historical price of all stock tickers not '
                           'in your list will be removed.'),
                    html.P('Currently, the system does not validate if there are empty data from Yahoo.'),
                    html.P('For example, if you input a date before the company got IPO, the system will report an error.'),
                    html.P('Note: The ending date cannot be today.'),
                    dcc.Input(
                        placeholder='Enter stock tickers',
                        type='text',
                        value='',
                        id='tickers-to-fetch'
                    ),
                    dcc.Input(
                        placeholder='Start date (YYYY-MM-DD)',
                        type='text',
                        value='',
                        id='fetch-start-date'
                    ),
                    dcc.Input(
                        placeholder='End date (YYYY-MM-DD)',
                        type='text',
                        value='',
                        id='fetch-end-date'
                    ),
                    html.Button('Refresh', id='fetch-button', n_clicks=0, className='button-primary', style={'margin-left': '10px'}),
                    html.H4('Current historical data in database'),
                    html.Div([
                        html.P(['Tickers which contain historical price info in database: ',
                                html.Span(id='ticker-list')
                                ])
                    ])
                ], className='six columns'),
                html.Div([
                    html.H4('Historical Price in Database:'),
                    dcc.Dropdown(
                        id='show-history-dropdown'
                    ),
                    dcc.Graph(id='finance-graph'),
                    # TODO
                    # html.Button('Export', id='export-button', n_clicks=0, className='button-primary')
                ], className='six columns')

            ], style=tab_style, selected_style=tab_selected_style),

            dcc.Tab(id='admin-database-tab', label='Database Management', children=[
                # html.Br(),
                html.H6('Please select a table in database to show its content:'),
                dcc.Dropdown(
                    id='app-1-dropdown',
                    options=[
                        {'label': 'DB table: {}'.format(i), 'value': i} for i in [
                            'Users', 'Orders', 'Portfolio', 'Position', 'Ticker', 'HistoricalPrice'
                        ]
                    ],
                    value='Users',
                    className='six columns'
                ),
                html.Div(id='app-1-display-value', className='six columns')
            ], style=tab_style, selected_style=tab_selected_style)
        ], style=tabs_styles)



        # dcc.Link('Go to App 2', href='/apps/app2')
    ])
    return admin_layout


layout = serve_layout()


@app.callback(
    Output('app-1-display-value', 'children'),
    [Input('app-1-dropdown', 'value')])
def display_value(value):
    if value is not None:
        division_query = (
            f'''
            SELECT *
            FROM {value}
            '''
        )

        conn = db.session.bind
        table2 = fetch_data(division_query, conn)

        return dash_table.DataTable(
            id='table1',
            columns=[{"name": i, "id": i} for i in table2.columns],
            data=table2.to_dict('records'),
            n_fixed_rows=1
        )
    return ''


@app.callback(
    [Output('ticker-list', 'children'),
     Output('show-history-dropdown', 'options')],
    [Input('fetch-button', 'n_clicks')],
    [State('tickers-to-fetch', 'value'),
     State('fetch-start-date', 'value'),
     State('fetch-end-date', 'value')])
def update_output(n_clicks, ticker, begin, end):
    if n_clicks >0 and ticker is not None and ticker != '':
        try:
            fecth_stock_info(ticker)
        except exc.IntegrityError as e:
            print('TickerID already exist in Ticker table')

        fetch_all_stocks(ticker, begin, end)

    tickerlist = db.session.query(HistoricalPrice.TickerID).group_by(HistoricalPrice.TickerID).all()
    if len(tickerlist) > 0:
        s = ''
        optionList =[]
        for temp in tickerlist:
            s = s + temp[0] + ' '
            optionList.append({'label': temp[0], 'value': temp[0]})

        return [s, optionList]
    else:
        return ['', []]


@app.callback(Output('finance-graph', 'figure'),
              [Input('show-history-dropdown', 'value')])
def display_value(value):
    if value is not None:
        result = db.session.query(HistoricalPrice._Date, HistoricalPrice.ClosingPrice).filter_by(TickerID=value).all()
        df = pd.DataFrame(result, columns=['Date', 'ClosingPrice'])

        data = [go.Scatter(
            x=df.Date,
            y=df['ClosingPrice'])]

        # py.iplot(data)
        # print('display_value')
        return {"data": data,
            "layout": go.Layout(
)}
    else:
        return None


@app.callback(
    Output('signal-2', 'children'),
    [Input('adduser-button', 'n_clicks')],
    [State('input-UserId', 'value'),
     State('input-UserPassword', 'value'),
     State('input-UserType', 'value'),
     State('input-UserFN', 'value'),
     State('input-UserLN', 'value')])
def add_user_submit(n_clicks, UserID, UserPassword, UserType, UserFN, UserLN):
    print('Got here')
    if n_clicks >0:
        ed_user = Users(UserID=UserID, UserPassword=UserPassword, UserFirstName=UserFN, UserLastName=UserLN, UserType=UserType)
        db.session.add(ed_user)
        ed_portfolio = Portfolio(UserID=UserID, Cash=1000000)
        db.session.add(ed_portfolio)
        db.session.commit()
    return 2


@app.callback(
    [Output('input2-UserPassword', 'value'),
     Output('input2-UserType', 'value'),
     Output('input2-UserFN', 'value'),
     Output('input2-UserLN', 'value')],
    [Input('user-dropdown', 'value')])
def modify_user_submit(selected):
    if selected is not None and selected != '':
        result = db.session.query(Users.UserID).all()
        if selected not in [x for x, in result]:
            return ['', '', '', '']
        else:
            passwd = db.session.query(Users.UserPassword).filter_by(UserID=selected).first()[0]
            utype = db.session.query(Users.UserType).filter_by(UserID=selected).first()[0]
            uFname = db.session.query(Users.UserFirstName).filter_by(UserID=selected).first()[0]
            uLname = db.session.query(Users.UserLastName).filter_by(UserID=selected).first()[0]
            return [passwd, utype, uFname, uLname]
    return ['', '', '', '']


@app.callback(
    Output('signal-1', 'children'),
    [Input('modifyuser-button', 'n_clicks')],
    [State('user-dropdown', 'value'),
     State('input2-UserPassword', 'value'),
     State('input2-UserType', 'value'),
     State('input2-UserFN', 'value'),
     State('input2-UserLN', 'value')])
def add_user_submit(n_clicks, UserID, UserPassword, UserType, UserFN, UserLN):
    print('Modified')
    if n_clicks >0 and UserID is not None and UserID !='':
        beg_user = db.session.query(Users.UserID).filter_by(UserID=UserID).first()
        if beg_user is not None:
            db.session.query(Users).filter(Users.UserID == UserID).update(
                {'UserPassword': UserPassword,
                 'UserType': UserType,
                 'UserFirstName': UserFN,
                 'UserLastName': UserLN}
            )
            # beg_user.UserPassword = UserPassword
            # beg_user.UserType = UserType
            # beg_user.UserFirstName = UserFN
            # beg_user.UserLastName = UserLN
        db.session.commit()
    return 1


@app.callback(
    Output('signal-3', 'children'),
    [Input('deluser-button', 'n_clicks')],
    [State('user-dropdown', 'value')])
def drop_user(n_clicks, userID):
    if n_clicks > 0:
        db.session.query(Users).filter_by(UserID= userID).delete()
        db.session.commit()
    return 3


@app.callback(
    [Output('user-data-area', 'children'),
     Output('num-of-users', 'children'),
     Output('user-dropdown', 'options')],
    [Input('signal-1', 'children'),
     Input('signal-2', 'children'),
     Input('signal-3', 'children')])
def update_user_list(value1, value2, value3):
    print('user refreshed')
    n_users = db.session.query(Users).count()
    if n_users is not None and n_users > 0:
        return [fetch_users(), n_users, fetch_users_options()]
    return [fetch_users(), 0, fetch_users_options()]
