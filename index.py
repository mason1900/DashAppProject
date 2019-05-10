import flask

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, db, Users
from apps import admin, main


# from flask_sqlalchemy import SQLAlchemy
# import urllib
# from sqlalchemy.ext.automap import automap_base
#
# # app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
# params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=DESKTOP-PMLC7BF\SQLEXPRESS;DATABASE=IST659;Trusted_Connection=yes;')
# app.server.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
# # app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db“
# app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app.server)
# # db.Model.metadata.reflect(bind=db.engine)
#
#
# # class Users(db.Model):
# #     __table__ = db.Model.metadata.tables['Users']
#
#
# # class HistoricalPrice(db.Model):
# #     __table__ = db.Model.metadata.tables['HistoricalPrice']
#
# Base = automap_base()
# Base.prepare(db.engine, reflect=True)
#
# Users = Base.classes.Users
# Ticker = Base.classes.Ticker
# Portfolio = Base.classes.Portfolio
# Position = Base.classes.Position
# Orders = Base.classes.Orders
# HistoricalPrice = Base.classes.HistoricalPrice


@app.server.route('/auth/login', methods=['POST'])
def route_login():
    data = flask.request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        flask.abort(401)

    result = db.session.query(Users).filter_by(UserID=username, UserPassword=password).first()
    if result is not None:
        print('Found')

        temp = db.session.query(Users.UserType).filter_by(UserID=username).first()
        if temp.UserType == 'admin' or temp.UserType == 'professor':
            rep = flask.redirect('/apps/admin')
        else:
            rep = flask.redirect('/apps/main')

        rep.set_cookie('auth-session', username)
    else:
        print('not found')
        rep = flask.redirect('/')


    # Return a redirect with


    # Here we just store the given username in a cookie.
    # Actual session cookies should be signed or use a JWT token.

    return rep


# create a logout route
@app.server.route('/auth/logout', methods=['POST'])
def route_logout():
    # Redirect back to the index and remove the session cookie.
    rep = flask.redirect('/')
    rep.set_cookie('auth-session', '', expires=0)
    return rep


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='session_id', style={'display': 'none'}),
    html.Div(id='current-username', style={'display': 'none'}),
    html.Div([
        html.Span('Virtual Stock Exchange', className='app-title'),
        dcc.LogoutButton(id='header-button', logout_url='/auth/logout', style={'float': 'right'})
    ], id='custom-header', className='header'),
    html.Div(id='page-content')
])


index_layout = html.Div([
    html.Div([
        html.H2('Login', className='stripe-4'),
        html.Form([
            dcc.Input(id='input-user', type='text', placeholder='Enter username', name='username',
                      style={'margin-top': '5%', 'margin-left': 'auto', 'margin-right': 'auto', 'display': 'block'}),
            dcc.Input(id='input-password', type='password', placeholder='Enter password', name='password',
                      style={'margin-top': '2%', 'margin-left': 'auto', 'margin-right': 'auto', 'display': 'block'}),
            html.Button('Login', id='button-login', type='submit', name='password',
                        style={'margin': '2% auto 5% auto', 'display': 'block'})

        ], action='/auth/login', method='post')
    ], className='LoginModule'),
    html.Div(id='dummy'),

    # dcc.Link('Navigate to "/apps/app1"', href='/apps/app1'),
    html.Br(),
    # dcc.Link('Navigate to "/apps/app2"', href='/apps/app2'),
])


@app.callback([Output('page-content', 'children'),
               Output('session_id', 'children')],
              [Input('url', 'pathname')])
def display_page(pathname):
    session_cookie = flask.request.cookies.get('auth-session')

    print(session_cookie)

    if pathname == '/apps/admin':
        if not session_cookie:
            return [index_layout, '']
        return [admin.layout, session_cookie]
    elif pathname == '/apps/main':
        if not session_cookie:
            return [index_layout, '']
        return [main.layout, session_cookie]
    elif pathname =='/':
        return [index_layout, '']
    elif pathname == '/success':
        return ['Login Success', '']
    else:
        return ['','']
    # else:
    #     return '404 Error Not Found'




# @app.callback(Output('dummy', 'children'),
#               [Input('button-login', 'n_clicks'),
#                Input('input-password', 'n_submit')],
#               [State('input-user', 'value'),
#                State('input-password', 'value')])
# def update_output(nb1, ns2, input1, input2):
#     return u'''
#         Input 1 is "{}",
#         and Input 2 is "{}"
#     '''.format( input1, input2)


if __name__ == '__main__':
    app.run_server(debug=True)