import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")
st.markdown("A clean, real-time stock tracker built for my Python Internship Project.")

# 2. Sidebar Settings (User Controls)
st.sidebar.header("Dashboard Configuration")

# Popular stock ticker selection + Custom input option
ticker_options = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "Custom"]
selected_ticker = st.sidebar.selectbox("Select a Stock Ticker", ticker_options)

if selected_ticker == "Custom":
    ticker_symbol = st.sidebar.text_input("Enter Custom Ticker (e.g., META, NFLX):", "META").upper()
else:
    ticker_symbol = selected_ticker

# Time interval selection
time_period = st.sidebar.selectbox("Select Time Period", ["1d", "5d", "1mo", "6mo", "1y"])

# Auto-refresh button (Simulating real-time updates)
refresh_button = st.sidebar.button("🔄 Refresh Data")

# 3. Data Fetching Logic (Requests via yfinance API)
@st.cache_data(ttl=10) # Cache data for 10 seconds to prevent spamming the API
def fetch_stock_data(ticker, period):
    try:
        # Fetching historical stock prices
        stock = yf.Ticker(ticker)
        
        # Determine the appropriate interval based on period for better granularity
        interval = "1m" if period == "1d" else "5m" if period == "5d" else "1d"
        df = stock.history(period=period, interval=interval)
        
        # Fetching current info/indicators
        info = stock.info
        return df, info
    except Exception as e:
        return None, None

# Load the data
df, info = fetch_stock_data(ticker_symbol, time_period)

# 4. Dashboard Display Layout
if df is not None and not df.empty and info is not None:
    
    # SECTION A: Financial Indicators (Key Metrics) 
    st.subheader(f"📊 {info.get('longName', ticker_symbol)} Financial Indicators")
    
    # Extract important metrics safely
    current_price = info.get('currentPrice', df['Close'].iloc[-1])
    previous_close = info.get('previousClose', df['Close'].iloc[0])
    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100
    
    # Display top-level metric boxes
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"${current_price:,.2f}", f"{price_change:+.2f} ({percent_change:+.2f}%)")
    col2.metric("Day High", f"${info.get('dayHigh', df['High'].max()):,.2f}")
    col3.metric("Day Low", f"${info.get('dayLow', df['Low'].min()):,.2f}")
    col4.metric("Market Cap", f"${info.get('marketCap', 0):,}")
    
    st.markdown("---")
    
    # SECTION B: Real-Time Visualization (Plotly Graphs) 
    st.subheader("📈 Real-Time Chart")
    
    # Chart selection option
    chart_type = st.radio("Select Chart Type", ["Line Chart", "Candlestick Chart"], horizontal=True)
    fig = go.Figure()
    
    if chart_type == "Line Chart":
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='#00FFCC')))
    else:
        fig.add_trace(go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'], name='Market Candles'))
        
    fig.update_layout(
        title=f"{ticker_symbol} Price Movement ({time_period})",
        xaxis_title="Time / Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    # SECTION C: Data View (Pandas DataFrame) 
    with st.expander("👁️ View Raw Historical Pandas Data Frame"):
        st.dataframe(df.tail(20)) # Shows last 20 rows of Pandas DataFrame
else:
    st.error(f"⚠️ Failed to fetch data for ticker '{ticker_symbol}'. Please make sure it's a valid stock symbol.")