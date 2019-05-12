-- Create tables
-- Can be created automatically by SQLAlchemy but this course requires SQL.

CREATE TABLE Users
(
UserID VARCHAR(20) PRIMARY KEY,
UserPassword VARCHAR(100) NOT NULL,
UserFirstName VARCHAR(30),
UserLastName VARCHAR(30),
UserType VARCHAR(20) NOT NULL,
);

CREATE TABLE Ticker
(
TickerID VARCHAR(20) PRIMARY KEY,
TickerShortName VARCHAR(80) NOT NULL,
TickerType VARCHAR(20) NOT NULL
);

CREATE TABLE Portfolio
(
UserID VARCHAR(20) PRIMARY KEY,
Cash float DEFAULT 1000000,
CONSTRAINT FK_User FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
CONSTRAINT chk_cash CHECK (Cash>=0),
);

CREATE TABLE Position
(
UserID VARCHAR(20) NOT NULL ,
TickerID VARCHAR(20) NOT NULL ,
Shares INT DEFAULT 0,
PositionType VARCHAR(10) NOT NULL,
CONSTRAINT FK_Position_User FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
CONSTRAINT FK_Position_Ticker FOREIGN KEY (TickerID) REFERENCES Ticker(TickerID),
CONSTRAINT chk_shares CHECK (Shares>=0),
CONSTRAINT pk_position PRIMARY KEY (UserId, TickerID, PositionType),
CONSTRAINT chk_position CHECK (PositionType='Buy' OR PositionType='Short')
);

CREATE TABLE Orders
(
OrderID INT IDENTITY PRIMARY KEY ,
UserID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Users(UserID) ON DELETE CASCADE,
TickerID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Ticker(TickerID),
OrderType VARCHAR(20) NOT NULL,
Shares INT NOT NULL ,
PriceType VARCHAR(10) NOT NULL,
Price float,
OrderDate DATETIME NOT NULL,
CONSTRAINT chk_ordershares CHECK (Shares>0),
CONSTRAINT chk_pricetype CHECK (PriceType='Market' OR PriceType='Limit' OR PriceType = 'Stop'),
CONSTRAINT chk_ordertype CHECK (OrderType IN ('Buy', 'Sell', 'Short', 'Buy to cover'))
);

CREATE TABLE HistoricalPrice
(
TickerID VARCHAR(20) NOT NULL,
_Date DATETIME NOT NULL,
ClosingPrice float NOT NULL,
Adj_Close float NOT NULL,
Volume bigint NOT NULL
CONSTRAINT pk_history PRIMARY KEY (TickerID, _Date),
CONSTRAINT FK_History_Ticker FOREIGN KEY (TickerID) REFERENCES Ticker(TickerID)
);

-- Insert admin, professor, and student users.
-- require at least one user.
-- Can be created automatically by SQLAlchemy but I did not implement it.
INSERT INTO Users
VALUES
('wmu100', 'mw2010a@gmail.com', 'Wei', 'Mu', 'admin'),
('ProfHoyos', 'hoyos@abc.com', 'H', 'Hoyos', 'professor'),
('ytong', 'ytong@def.com', 'Yuntong', 'Liu', 'student'),
('admin', 'root123', 'admin', 'user', 'admin');

-- Insert some random tickers
-- This is not required because the web app program automatically fix it.
INSERT INTO Ticker
VALUES
('AAPL', 'Apple, Inc.', 'Stock'),
('IBM', 'International Business Machines', 'Stock'),
('MCD', 'McDonald"s Corporation', 'Stock');


-- Insert initial portfolio for one of the users
-- This is not required because the web app program automatically fix it.
INSERT INTO Portfolio
VALUES
('wmu100', 1000000);



-- Who are the current users of the system? 
SELECT * FROM Users;

-- How many students have been registered in this system?
select COUNT(UserID) AS NumberOfStudents FROM Users;



SELECT * FROM Ticker
SELECT * FROM Portfolio
SELECT * FROM Position
SELECT * FROM Orders
SELECT * FROM HistoricalPrice

