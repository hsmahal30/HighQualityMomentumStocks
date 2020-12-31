from secrets import API_TOKEN
import pandas as pd
import iexfinance
from scipy import stats
import math
import plotly.express as px
import os
from iexfinance.stocks import Stock,get_historical_data
import requests
from statistics import mean

os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'

def get_stock_price(ticker):
    """ Get indivdual stock prices

    Args:
        ticker : Stock ticker symbols 

    Returns:
        Current price of stock entered 
    """
    ticker.upper()
    price = Stock(ticker,token = API_TOKEN)
    return price.get_price()

def get_batch_price(tickers):
    """Get prices of multiple stocks by making batch API call

    Args:
        tickers: Stock ticker symbols 

    Returns:
        Current price of each stock 
    """
    batch = Stock(tickers,token = API_TOKEN)
    return batch.get_price()

def stock_quote(symbol):
    """ Get 

    Args:
        symbol ([type]): [description]

    Returns:
        [type]: [description]
    """
    quote = Stock(symbol,token=API_TOKEN)
    quote = quote.get_quote()
    return quote

def get_stats(symbol):
    """[summary]

    Args:
        symbol ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = Stock(symbol,token=API_TOKEN)
    data = data.get_key_stats()
    return data

def return_percentile(df, time_periods):
    """Calculate percent return of each stock in the specified time period and create new columns in dataframe with calculation for each stock

    Args:
        df : Pandas dataframe
        time_periods: list of time periods to be examined 
    """
    for row in df.index:
        for time_period in time_periods:
            df.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(df[f'{time_period} Price Return'], df.loc[row, f'{time_period} Price Return'])/100

def calculate_hqm(df, time_periods):
    """Calculate the quality of the momentum of each stock using the movement data from the specified time periods 

    Args:
        df : Pandas dataframe 
        time_periods : list of time periods to be examined
    """
    for row in df.index:
        momentum_percentiles = []
        for time in time_periods:
            momentum_percentiles.append(df.loc[row,f'{time} Return Percentile'])
        df.loc[row,'HQM Score'] = mean(momentum_percentiles)

def main():
    #FILE INPUT 
    try:
        stocks_file = pd.read_csv('FILEPATH')
    except FileNotFoundError:
        print("File not found. Check file path")

    #LIST FOR TICKER SYMBOLS
    tickers = []
    for stock in stocks_file['Ticker']:
        tickers.append(stock)

    #API CALLS
    current_prices = get_batch_price(tickers)
    quote = stock_quote(tickers)
    stock_returns = get_stats(tickers)

    #Lists to hold API Data
    market_cap = []
    one_year = []
    six_month = []
    three_month = []
    one_month = []

    #Parse data from API and store in lists 
    for symbol in tickers:
        market_cap.append(quote[symbol]['marketCap'])
        one_year.append(stock_returns[symbol]['year1ChangePercent'])
        six_month.append(stock_returns[symbol]['month6ChangePercent'])
        three_month.append(stock_returns[symbol]['month3ChangePercent'])
        one_month.append(stock_returns[symbol]['month1ChangePercent'])

    #CREATE INITIAL DATA FRAME FOR STOCK DATA
    col = ['Ticker','Price']
    df = pd.DataFrame(current_prices.items(),columns=col)

    #Time periods for stock data to be examined 
    time_periods = [
        'One-Year',
        'Six-Month',
        'Three-Month',
        'One-Month'
    ]

    #Create new colummns in dataframe containing data parsed from API for each stock
    df['Market Cap'] = market_cap
    df['One-Year Price Return'] = one_year
    df['One-Year Return Percentile'] = 0
    df['Six-Month Price Return'] = six_month
    df['Six-Month Return Percentile'] = 0
    df['Three-Month Price Return'] = three_month
    df['Three-Month Return Percentile'] = 0
    df['One-Month Price Return'] = one_month
    df['One-Month Return Percentile'] = 0
    df['HQM Score'] = 0

    #Calculate return percentile and quality of momentum for each stock
    return_percentile(df,time_periods)
    calculate_hqm(df,time_periods)

    #Convert data frame to excel sheet 
    df.to_excel("FILEPATH", sheet_name = 'Sheet_name_1')

if __name__ == "__main__":
    main()
    

