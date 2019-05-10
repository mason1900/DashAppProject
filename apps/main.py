import flask
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, db, HistoricalPrice, Position, Portfolio, Orders, Users
import pandas as pd
import plotly.graph_objs as go
import pandas as pd
import dash_table
from datetime import datetime as dt, timedelta

DEFAULT_INITIAL_CASH = 1000000


def fetch_stocks_available():
    result = db.session.query(HistoricalPrice.TickerID).group_by(HistoricalPrice.TickerID).all()
    if result is not None and len(result) > 0:
        return [x for x, in result]
    else:
        return []


def fetch_stocks_available_options():
    tickerlist = fetch_stocks_available()
    return [{'label':i,  'value':i} for i in tickerlist]


def fetch_remain_cash(current_user):
    # current_user = flask.request.cookies.get('auth-session')
    result = db.session.query(Portfolio.Cash).filter_by(UserID=current_user).first()
    if result is not None and (len(result) > 0):
        return True, result[0]
    else:
        return False, ''


def fetch_user_position(userId):
    # .all() return empty list if query returns no results
    sql = db.session.query(Position).filter_by(UserID=userId).statement
    df = pd.read_sql(sql=sql, con=db.session.bind)
    df.columns = ['UserID', 'Ticker', 'Shares', 'PositionType']
    # df = pd.DataFrame(result, columns=['UserID', 'Ticker', 'PositionType', 'Shares'])
    return df


def fetch_order_history(userId):
    # .all() return empty list if query returns no results
    sql = db.session.query(Orders).filter_by(UserID=userId).statement
    df = pd.read_sql(sql=sql, con=db.session.bind)
    # df = pd.DataFrame(result, columns=['OrderID', 'UserID', 'TickerID', 'OrderType', 'Shares', 'PriceType', 'Price', 'Date'])
    return df


def reset_order(userId):
    db.session.query(Orders).filter_by(UserID=userId).delete()
    db.session.query(Portfolio).filter_by(UserID=userId).delete()
    db.session.query(Position).filter_by(UserID=userId).delete()
    db.session.commit()


# similar to Django
# sometimes need to del the instance before next use
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def add_order(_order):
    # TODO: short sell buy to cover
    # Todo: try catch
    # insert order
    db.session.add(_order)
    # get corresponding price
    price_instance = db.session.query(HistoricalPrice).filter_by(TickerID=_order.TickerID, _Date=_order.OrderDate).first()
    if price_instance is None:
        db.session.rollback()
        msg = 'no corresponding price in db'
        print(msg)
        return False, msg
    price = price_instance.ClosingPrice

    # Sell: check Position Shares >= Order shares
    if _order.OrderType == 'Sell':
        p_instance = db.session.query(Position.Shares).filter_by(
            UserID=_order.UserID, TickerID=_order.TickerID, PositionType='Buy').first()
        if p_instance is None or (p_instance.Shares < int(_order.Shares)):
            msg = 'Selling more shares than available'
            print(msg)
            return False, msg

    # get or set portfolio
    portfolio = get_or_create(db.session, Portfolio, UserID=_order.UserID)
    if _order.OrderType == 'Buy':
        portfolio.Cash = portfolio.Cash - float(_order.Shares) * price
    elif _order.OrderType == 'Sell':
        portfolio.Cash = portfolio.Cash + float(_order.Shares) * price
    # get or set position
    position = get_or_create(db.session, Position,
                             UserID=_order.UserID, TickerID=_order.TickerID, PositionType='Buy')
    if _order.OrderType == 'Buy':
        position.Shares = position.Shares + int(_order.Shares)
    elif _order.OrderType == 'Sell':
        position.Shares = position.Shares - int(_order.Shares)
    # clean up
    db.session.commit()
    del portfolio
    del position
    return True, ''

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


main_layout= html.Div([
    # Left pane
    html.Div([
        html.Div([
            html.H4('Stock simulation:'),
            html.Label('Symbol', htmlFor='input-Symbol'),
            dcc.Input(
                placeholder='Enter symbol, e.g. AAPL',
                type='text',
                value='',
                id='input-Symbol'
            ),
            html.Label('Order Type', htmlFor='order-dropdown'),
            # This Div does nothing but fix rendering problem.
            html.Div([
                # TODO: short selling
                dcc.Dropdown(
                    id='order-dropdown',
                    options=[
                        {'label': 'Buy', 'value': 'Buy'},
                        {'label': 'Sell', 'value': 'Sell'},
                        {'label': 'Short', 'value': 'Short', 'disabled': True},
                        {'label': 'Buy to cover', 'value': 'Buy to cover', 'disabled': True}
                    ],
                    value='Buy',
                    searchable=False,
                    className='three columns'
                ),
            ], className='twelve columns'),
            html.Label('Shares', htmlFor='input-shares'),
            dcc.Input(
                id='input-shares',
                placeholder='Enter # of shares, e.g. 42',
                type='text',
                value=0,
            ),
            html.Label('Price Type', htmlFor='pricetype-dropdown'),
            html.Div([
                dcc.Dropdown(
                    id='pricetype-dropdown',
                    options=[{'label': i, 'value': i} for i in ['Market', 'Limit', 'Stop']],
                    value='Market',
                    className='three columns',
                    searchable=False,
                ),
            ], className='twelve columns'),
            html.Label('Price', htmlFor='input-order-price'),
            html.Div([
                dcc.Input(
                    id='input-order-price',
                    placeholder='Enter price, e.g. 50.00',
                    type='text',
                    value='',
                )
            ], className='twelve columns'),
            html.Label('Order Date', htmlFor='input-order-date'),
            html.Div([
                dcc.DatePickerSingle(
                    id='date-picker-main',
                    display_format='YYYY-MM-DD',
                    initial_visible_month=dt(2010, 1, 1),
                    max_date_allowed=dt.today() - timedelta(days=1),
                    date=str(dt(2010, 1, 25))
                 ),
                html.P(id='date-range-warning', style={'color': 'red'})
            ], className='twelve columns'),
            html.Button('Place Order', id='order-button', n_clicks=0, className='button-primary',
                        style={'margin-top': '10px'}),
            html.P(),
            html.P('Tickers available for simulation: '),
            html.Span(id='main-ticker-list'),
            html.P(id='order-message'),
        ], className='six columns'),

        # middle pane
        html.Div([
            html.H4('Cash remaining:'),
            html.P(id='remain-cash'),
            html.H4('Overall gain:'),
            html.P(id='overall-gain'),
            html.H4('Overall return:'),
            html.P(id='overall-return'),
            html.H4('Reset all orders:'),
            html.Button('Reset', id='reset-order-button', className='button-primary',
                        style={'background-color': '#fa4f56'})
        ], className='six columns')
    ], className='six columns'),

    # Right pane
    html.Div([
        html.H4('Historical Price:'),
        dcc.Dropdown(
            id='page-2-dropdown',
            options=fetch_stocks_available_options()
        ),
        html.Div([dcc.Graph(id='my-graph')], id='page-2-display-value'),
        dcc.Checklist(
            id='price-display-option',
            options=[
                {'label': 'Adjusted Closing Prrice', 'value': 'Adj_Close'},
                {'label': '42-day moving average', 'value': '42d'},
                {'label': '252-day moving average', 'value': '252d'}
            ],
            values=['Adj_Close'],
            labelStyle={'display': 'inline-block'}
        )
    ], className='six columns'),
], className='twelve columns')


holding_layout=html.Div([
    # html.H4('Current holdings:'),
    # data = [go.Scatter(
    # x=df.Date,
    # y=df['ClosingPrice'])]
    # dcc.Graph(figure={'data':'', 'layout': go.Layout()})
    html.Div([
        html.Div([
            html.H4('Current holdings'),
            html.Div(id='position-table'),
            html.H4('Order history'),
            html.Div(id='order-table')
        ], className='six columns'),
        # TODO
        # html.Div([
        #     dcc.Graph(id='holding-graph')
        # ], className='six columns')
    ], className='twelve columns')

])


def serve_layout():
    layout = html.Div([
        dcc.Tabs(id='user-tabs', children=[
            dcc.Tab(id='user-main-tab', label='Stock simulation', value='main-tab',children=[
                main_layout
                ], style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(id='user-holding-tab', label='Your holdings', value='holding-tab', children=[
                holding_layout
            ], style=tab_style, selected_style=tab_selected_style)
        ], value='main-tab', style=tabs_styles),
        html.Footer(id='admin-redir-link'),
        html.Div(id='signal', style={'display': 'none'}),
        html.Div(id='signal2', style={'display': 'none'}),
    ])
    return layout


layout = serve_layout()


@app.callback(Output('my-graph', 'figure'),
              [Input('page-2-dropdown', 'value'),
               Input('price-display-option', 'values')])
def display_value(ticker, values):
    result = db.session.query(HistoricalPrice._Date, HistoricalPrice.Adj_Close).filter_by(TickerID=ticker).all()
    if result is not None and len(result) > 0:
        df = pd.DataFrame(result, columns=['Date', 'Adj_Close'])
        df['42d'] = df['Adj_Close'].rolling(center=False, window=42).mean()
        df['252d'] = df['Adj_Close'].rolling(center=False, window=252).mean()
        data = []
        for temp in values:
            data = data + [go.Scatter(x=df.Date, y=df[temp], name =temp)]
        # data = [go.Scatter(
        #     x=df.Date,
        #     y=df['Adj_Close'])]
        return {"data": data,
                "layout": go.Layout()}
    else:
        return {}


@app.callback([Output('input-order-price', 'disabled'),
               Output('input-order-price', 'style')],
              [Input('pricetype-dropdown', 'value')])
def disable_price_input(value):
    if value == 'Market':
        return ['disabled', {'background-color': 'lightgray'}]
    else:
        return [False, {}]


@app.callback([Output('remain-cash', 'children'),
               Output('overall-gain', 'children'),
               Output('overall-return', 'children'),
              Output('main-ticker-list', 'children')],
              [Input('session_id', 'children'),
               Input('signal', 'children'),
               Input('signal2', 'children')])
def display_remain_cash(session_user, signal, signal2):
    tickerlist = db.session.query(HistoricalPrice.TickerID).group_by(HistoricalPrice.TickerID).all()
    status, cash = fetch_remain_cash(session_user)
    gain = 0
    _return = 0
    if status:
        gain = cash - DEFAULT_INITIAL_CASH
        _return = (cash - DEFAULT_INITIAL_CASH) / DEFAULT_INITIAL_CASH

    if len(tickerlist) > 0:
        s = ''
        for temp in tickerlist:
            s = s + temp[0] + ' '
        return [cash, gain, "{:.1%}".format(_return), s]
    return [cash, gain, "{:.1%}".format(_return), '']


@app.callback(Output('admin-redir-link', 'children'),
              [Input('session_id', 'children')])
def display_redir_link(session_user):
    result = db.session.query(Users.UserType).filter_by(UserID=session_user).first()
    if session_user is None:
        return ''
    if result.UserType == 'admin' or result.UserType == 'professor':
        link = html.A('Go back to admin page', href='/apps/admin')
        return link
    else:
        return ''


# @app.callback(Output('holding-graph', 'figure'),
#               [Input('user-tabs', 'value')])
# def show_selected(tab_name):
#     # TODO: holding graph
#     print(tab_name)
#     if tab_name == 'holding-tab':
#         data = go.Bar(
#             x=['2016', '2017', '2018'],
#             y=[300, 400, 700],
#             base=0,
#             marker=dict(
#               color='blue'
#             ),
#             name='revenue'
#         )
#         return {'data': [data], 'layout': go.Layout()}
#     else:
#         return {}


@app.callback([Output('position-table', 'children'),
               Output('order-table', 'children')],
              [Input('user-tabs', 'value')],
              [State('session_id', 'children')])
def show_selected(tab_name, session_id):
    # TODO
    print(tab_name)
    if tab_name == 'holding-tab':
        df = fetch_user_position(session_id)
        df_order = fetch_order_history(session_id)
        return [dash_table.DataTable(
            id='datatable-position',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            n_fixed_rows=1
        ), dash_table.DataTable(
            id='datatable-order',
            columns=[{"name": i, "id": i} for i in df_order.columns],
            data=df_order.to_dict('records'),
            n_fixed_rows=1
        )]
    else:
        return ['','']


@app.callback([Output('user-tabs', 'value'),
               Output('signal', 'children')],
              [Input('reset-order-button', 'n_clicks')],
              [State('session_id', 'children')])
def reset_order_submit(n_clicks, session):
    if n_clicks > 0:
        reset_order(session)
        print('reset order')
        return ['main-tab', 'reset-order']
    print('Got reset callback')
    return ['main-tab', '']


@app.callback(Output('date-range-warning', 'children'),
              [Input('date-picker-main', 'date')])
def validate_order_date(date):
    print(str(date))
    result = db.session.query(HistoricalPrice).filter_by(_Date=date).first()
    if result is None:
        return 'The date is not in the Historical Price database. This day may not be a trading day, or it ' \
               'is below or above the range of the current available data. Please select another date or contact ' \
               'admin to refresh data.'


@app.callback([Output('order-message', 'children'),
               Output('signal2','children')],
              [Input('order-button', 'n_clicks')],
              [State('input-Symbol', 'value'),
               State('order-dropdown', 'value'),
               State('input-shares', 'value'),
               State('pricetype-dropdown', 'value'),
               State('input-order-price', 'value'),
               State('date-picker-main', 'date'),
               State('session_id', 'children')])
def place_order_submit(n_clicks, symbol, ordertype, shares, pricetype, price, date, session_id):
    if n_clicks > 0:
        if pricetype == 'Limit' or pricetype == 'Stop':
            msg = 'Limit/Stop orders not supported yet.'
            return [msg, '']

        result = db.session.query(HistoricalPrice).filter_by(TickerID=symbol).first()
        if result is None:
            msg = 'Ticker does not have corresponding historical price in the database. ' \
                  'Please input another ticker or contact admin to refresh database'
            return [msg, '']

        order = Orders(UserID=session_id, TickerID=symbol.upper(), OrderType=ordertype, Shares=shares, PriceType=pricetype,
                       Price=price, OrderDate=date)
        status, msg = add_order(order)
        if status == True:
            return ['Success! Purchased' + symbol + ' at ' + str(date) + ' Timestamp: ' +str(dt.today()), 'place']
        else:
            return [msg, '']
    return ['', '']

