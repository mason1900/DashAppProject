# Lightweight Financial Data Management System

Yet another web app coded using Python Dash framework.

As Yahoo! Finance stopped providing Yahoo Stock API for historical price data since 2017, it becomes difficult for general users to stably fetch open-to-public financial data from the Internet. Although multiple workarounds has been provided by developers and companies, many of the solutions are commercially licensed and require subscriptions fee. Others require uses some knowledge in programming (such as Python or VBA) to get it working with existing system.

The object of this project is to design and implement a lightweight financial data management and trading simulation system. The basic functions of the system are as follows:

1. Allow users to input their orders and simulate trading behavior using historical financial data. Users can also place orders and wait until new data is available in the future. In this scenario, it works like a “virtual stock exchange”.

2. automatically pull, scrape, and store real time and historical financial data from open-to-public sources provided on the internet. Sources include Yahoo! Finance and IEX Finance. Financial data includes real time stock prices, historical prices, basic statistics, financials, and options. The web-scraping part for Yahoo! Finance is based on an existing Excel tool written by one of the team members. The tool is currently in-use by the professor of Financial Modeling class.
3. Show the users’ positions at end and calculate returns using simulated order history.
4. provide interface for academic users to easily summarize data and generate Excel spreadsheets.

## Technical Infrastructure

The project is implemented using SQL server Express as backend and Python Dash as the frontend which interacts with user as a web application. Some other Python packages and frameworks are also used in this project, such as “Plotly”, “SQLAlchemy”, “Flask”, “Flask-SQLAlchemy”, and “fix-yahoo-finance”.

![Overview](.\docs\Overview.png)

The Dash framework is built upon React.js as the browser front end and Flask as the web server backend. Plotly is a visualization framework which involves interaction with Dash. SQLAlchemy is a Python SQL toolkit which provides interfaces including SQL Expression Language and ORM (Object Relational Mapper)  ,and Flask-SQLAlchemy is a wrapper which manages SQLAlchemy sessions within Dash/Flask.

Although SQLAlchemy can create the tables on-the-fly by using ORM, which is better and easier to implement, however, as per the requirement of the course, the tables are created separately before reflecting into ORM with automap extension.

### About Dash

Dash is a Python framework which allows programmers/data scientists to quickly build data science web application in pure Python, without the knowledge of JavaScript and CSS. (However, in our system we wrote some CSS to fix some rendering issues. ) Dash is designed for single-page apps, but it does allow multiple pages, in which the contents are dynamically loaded without refreshing. This project is an example of a multi-page web app. **index.py** is the entry point. **app.py** connects to the database and initialize ORM with automap extension of SQLAlchemy. **main.py** and **admin.py** are app pages. 

Dash runs Flask as the backend webserver, but Dash allows multi-process and scaling (such as using Gunicorn), so it can be deployed to production server.

## Usage

First, create the tables with **SQL_Create_Table_Insert_Sample.sql**. Use sqlcmd, SQL Server Management Studio or any other SQL Server Management toolkit.

Then, edit the connection string within **app.py**. You may want to create a DSN.

Third, run the application by executing the following code:

```bash
Python index.py
```

The server should run on `localhost` with port number `8050` in `debug mode`. **Debug mode** allows developers to examine the callback graphs and error messages and runs in single process mode.

Currently, this project possesses some **security risks**, including session hijacking and SQL injection. Do not use it in a production server before the development is 100% complete. To test the production mode, change `app.run_server(debug=True)` to `app.run_server(debug=False)` in **index.py**. To test multiple process mode (Gunicorn), follow the instructions on [Dash official documents.](https://dash.plot.ly/deployment)

## TODO

- Implement Short/Buy to Cover orders and Margin Call
- Implement Limit and Stop orders
- Implement multiple validations for user inputs
- Implement visualization for Holdings
- Implement fetching of current stock info 
- Implement secure login system
- Fix security issues
- Allow users to register and change password
- Fix coding style
- Implement export to csv function on the financial data management page
- Allow general users to fetch financial financial data
- Migrate to MySQL
- Create Docker image