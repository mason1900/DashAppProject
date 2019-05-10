import urllib
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = dash.Dash()
# app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=DESKTOP-PMLC7BF\SQLEXPRESS;DATABASE=IST659;Trusted_Connection=yes;')
app.server.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
# app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db“
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.server)

# server = app.server


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


app.layout = html.Div(
    [
        html.H4("username"),
        dcc.Input(id="username", placeholder="enter username", type="text"),
        html.H4("email"),
        dcc.Input(id="email", placeholder="enter email", type="email"),
        html.Button("add user", id="add-button"),
        html.Hr(),
        html.Button('refresh',id='refresh-button'),
        html.Button('UsersButton', id='pd-button'),
        html.Div(id='test-pd'),
        html.H3("users"),
        html.Div(id="users"),
    ]
)


def fetch_data(q, session):
    result = pd.read_sql(
        sql=q,
        con=session
    )
    return result

# @app.callback(
#     Output("users", "children"),
#     [Input("add-button", "n_clicks")],
#     [State("username", "value"), State("email", "value")],
# )
# def add_and_show_users(n, username, email):
#     if n is not None:
#         # if button clicked, add user
#         db.session.add(User(username=username, email=email))
#         db.session.commit()
#
#     # get all users in database
#     users = db.session.query(User).all()
#     return [
#         html.Div(
#             [
#                 html.Span([html.H5("Username: "), u.username]),
#                 html.Span([html.H5("Email: "), u.email]),
#             ]
#         )
#         for u in users
#     ]

    # division_query = (
    #     f'''
    #     SELECT *
    #     FROM [Users]
    #     '''
    # )
    # conn= db.session.bind
    # temp = fetch_data(division_query, conn)

@app.callback(
    Output('test-pd', 'children'),
    [Input('pd-button', 'n_clicks')]
)
def output_tables(n):
    if n is None:
        return None
    division_query = (
        f'''
        SELECT *
        FROM [Users]
        '''
    )
    conn = db.session.bind
    table1 = fetch_data(division_query, conn)
    return dash_table.DataTable(
        id='table1',
        columns=[{"name": i, "id": i} for i in table1.columns],
        data=table1.to_dict('records'),
        n_fixed_rows=1
    )


@app.callback(
    Output("users", "children"),
    [Input("add-button", "n_clicks"),
     Input('refresh-button', 'n_clicks')],
    [State("username", "value"), State("email", "value")],
)
def add_and_show_users(n, m, username, email):
    ctx= dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-button':
        # if button clicked, add user
        db.session.add(Users(username=username, email=email))
        db.session.commit()

    # get all users in database
    users = db.session.query(Users).all()
    return [
        html.Div(
            [
                html.Span([html.H5("Username: "), u.username]),
                html.Span([html.H5("Email: "), u.email]),
            ]
        )
        for u in users
    ]


if __name__ == "__main__":
    db.create_all()
    app.run_server()