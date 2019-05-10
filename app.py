import dash
from flask_sqlalchemy import SQLAlchemy
import urllib
from sqlalchemy.ext.automap import automap_base
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=DESKTOP-PMLC7BF\SQLEXPRESS;DATABASE=IST659;Trusted_Connection=yes;')
app.server.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
# app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db“
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.server)
# db.Model.metadata.reflect(bind=db.engine)


# class Users(db.Model):
#     __table__ = db.Model.metadata.tables['Users']


# class HistoricalPrice(db.Model):
#     __table__ = db.Model.metadata.tables['HistoricalPrice']

Base = automap_base()
Base.prepare(db.engine, reflect=True)

Users = Base.classes.Users
Ticker = Base.classes.Ticker
Portfolio = Base.classes.Portfolio
Position = Base.classes.Position
Orders = Base.classes.Orders
HistoricalPrice = Base.classes.HistoricalPrice