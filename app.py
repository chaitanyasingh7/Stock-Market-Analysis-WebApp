import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

# Function to fetch stock data from Yahoo Finance
def fetch_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    data = yf.download(ticker, start=start_date, end=end_date)
    # data = stock.history(start=start_date, end=end_date)
    data.reset_index(inplace=True)
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    data.set_index('Date', inplace=True)

    # Fundamental data
    financials = stock.financials.T
    balance_sheet = stock.balance_sheet.T
    cashflow = stock.cashflow.T

    return data, financials, balance_sheet, cashflow

# Function to plot historical stock prices
def plot_stock_prices(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))

    fig.update_layout(title='Stock Prices',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

# Function to plot candlestick chart
def plot_candlestick(data):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])
    fig.update_layout(title='Candlestick Chart', xaxis_title='Date', yaxis_title='Price')
    st.plotly_chart(fig)

# Function to display metrics
def display_metrics(df):
    st.subheader('Important Metrics')
    
    st.write(f"**Current Price:** ${df['Close'].iloc[-1]:.2f}")
    st.write(f"**52-Week High:** ${df['High'].max():.2f}")
    st.write(f"**52-Week Low:** ${df['Low'].min():.2f}")
    st.write(f"**Average Volume:** {df['Volume'].mean():.2f}")
    st.write(f"**30-Day Return:** {(df['Close'].iloc[-1] / df['Close'].iloc[-30] - 1) * 100:.2f}")

#display financial ratios
def display_financial_ratios(ticker, stock):
    st.write(f"Financial Ratios for {ticker}:")
    info = stock.info
    ratios = {
        'P/E Ratio': info.get('trailingPE', 'N/A'),
        'EPS (TTM)': info.get('trailingEps', 'N/A'),
        'Dividend Yield': info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A'
    }
    st.write(pd.DataFrame(list(ratios.items()), columns=['Ratio', 'Value']))


# Function to plot volume bar chart
def plot_volume_histogram(data):
    # Create a histogram for the 'Volume' column
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=data['Volume'], nbinsx=50, name='Volume'))
    
    # Update layout
    fig.update_layout(title='Stock Volume Histogram',
                      xaxis_title='Volume',
                      yaxis_title='Frequency',
                      bargap=0.2)
    st.plotly_chart(fig)


 # Plot correlation heatmap   
def plot_correlation_heatmap(data):
    if data.empty:
        raise ValueError("DataFrame is empty")

    # Compute the correlation matrix
    corr_matrix = data.corr()

    # Create the heatmap
    fig = px.imshow(corr_matrix, 
                    text_auto=True,
                    title='Correlation Heatmap')

    st.plotly_chart(fig)


# Main Streamlit app function
def main():
    st.title('Stock Price Analysis')
    
    st.sidebar.header('Welcome! Choose a stock to analyze.')
    
    ticker = st.sidebar.text_input('Stock Ticker Symbol', 'AAPL').upper()
    stock = yf.Ticker(ticker)
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    
    st.sidebar.text('Fetching data...')
    data, financials, balance_sheet, cashflow = fetch_data(ticker, start_date, end_date)
    
    if data.empty:
        st.error('No data found for the given ticker.')
    else:
        st.subheader(f'{ticker} Stock Data')
        st.write(data.tail().iloc[::-1])
        
        # Display important metrics
        display_metrics(data)

        # Plot historical stock prices
        plot_stock_prices(data)

        #display financial ratios 
        display_financial_ratios(ticker, stock)

        # Plot candlestick chart
        plot_candlestick(data)

        # Plot volume bar chart
        plot_volume_histogram(data)

        # Correlation heatmap 
        plot_correlation_heatmap(data)


            

if __name__ == '__main__':
    main()

