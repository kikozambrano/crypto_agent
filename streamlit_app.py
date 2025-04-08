import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

# App title
st.title("📊 Crypto Indicator Dashboard")

# Sidebar inputs
st.sidebar.header("Settings")

# Cryptocurrency selection
crypto = st.sidebar.selectbox("Select a cryptocurrency", ["BTC-USD", "ETH-USD", "SOL-USD"])
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))

# Indicator parameters
sma_period = st.sidebar.slider("SMA Period", min_value=5, max_value=200, value=50)
rsi_period = st.sidebar.slider("RSI Period", min_value=5, max_value=30, value=14)
macd_fast = st.sidebar.slider("MACD Fast", 5, 20, 12)
macd_slow = st.sidebar.slider("MACD Slow", 20, 50, 26)
macd_signal = st.sidebar.slider("MACD Signal", 5, 20, 9)

st.sidebar.markdown("---")
st.sidebar.subheader("Labeling Parameters")

holding_period = st.sidebar.slider("Holding Period (Days)", 1, 30, 5)
buy_threshold = st.sidebar.slider("Price Increase for BUY (%)", 1, 20, 5)
sell_threshold = st.sidebar.slider("Price Drop for SELL (%)", 1, 20, 5)

# Function to download historical data
def download_data(ticker, start_date):
    try:
        data = yf.download(ticker, start=start_date, interval="1d")
        if data.empty:
            raise ValueError("No data fetched")
        return data
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

# Function to add indicators to the data
def add_indicators(data, sma_period, rsi_period, macd_fast, macd_slow, macd_signal):
    close = data["Close"]
    data["SMA"] = ta.trend.sma_indicator(close, window=sma_period)
    data["RSI"] = ta.momentum.rsi(close, window=rsi_period)
    macd = ta.trend.MACD(close, window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_signal)
    data["MACD"] = macd.macd_diff()
    data["MACD_line"] = macd.macd()
    data["MACD_signal"] = macd.macd_signal()
    return data

# Function to label data
def label_data(df, holding_period, buy_threshold, sell_threshold):
    df = df.copy()

    # Create future close column and ensure alignment
    df["Future_Close"] = df["Close"].shift(-holding_period)

    # Calculate future return and ensure it's a Series
    df["Future_Return"] = (df["Future_Close"] - df["Close"]) / df["Close"]

    # Drop rows with NaNs to avoid index misalignment
    df = df.dropna(subset=["Future_Return"])

    # Initialize signal column
    df["Signal"] = 0
    df.loc[df["Future_Return"] >= buy_threshold / 100, "Signal"] = 1
    df.loc[df["Future_Return"] <= -sell_threshold / 100, "Signal"] = -1

    return df

# Download historical data
data = download_data(crypto, start_date)

# Add indicators
data = add_indicators(data, sma_period, rsi_period, macd_fast, macd_slow, macd_signal)

# Apply labeling
data = label_data(data, holding_period, buy_threshold, sell_threshold)

# Optional: show raw data
if st.checkbox("Show raw data"):
    st.dataframe(data.tail(20))

# Function to plot price chart with indicators and signals
def plot_price_chart(data, crypto, sma_period):
    st.subheader(f"{crypto} Price and Indicators")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data["Close"], label="Close Price", color='blue')
    ax.plot(data.index, data["SMA"], label=f"SMA {sma_period}", color='black')
    ax.set_ylabel("Price (USD)")
    ax.set_xlabel("Date")
    ax.grid()
    buy_signals = data[data["Signal"] == 1]
    sell_signals = data[data["Signal"] == -1]
    ax.scatter(buy_signals.index, buy_signals["Close"], label="BUY", marker="^", color="green", s=100)
    ax.scatter(sell_signals.index, sell_signals["Close"], label="SELL", marker="v", color="red", s=100)
    ax.legend()
    st.pyplot(fig)

# Function to plot RSI chart
def plot_rsi_chart(data):
    st.subheader("RSI")
    fig_rsi, ax_rsi = plt.subplots(figsize=(12, 2))
    ax_rsi.plot(data.index, data["RSI"], label="RSI", color='orange')
    ax_rsi.axhline(70, color='red', linestyle='--')
    ax_rsi.axhline(30, color='green', linestyle='--')
    ax_rsi.set_ylabel("RSI")
    ax_rsi.grid()
    st.pyplot(fig_rsi)

# Function to plot MACD chart
def plot_macd_chart(data):
    st.subheader("MACD")
    fig_macd, ax_macd = plt.subplots(figsize=(12, 4))
    ax_macd.plot(data.index, data["MACD_line"], label="MACD Line", color='blue')
    ax_macd.plot(data.index, data["MACD_signal"], label="Signal Line", color='red')
    ax_macd.bar(data.index, data["MACD"], label="Histogram", color='purple', alpha=0.4)
    ax_macd.axhline(0, color='gray', linestyle='--')
    ax_macd.set_ylabel("MACD")
    ax_macd.legend()
    ax_macd.grid()
    st.pyplot(fig_macd)

# Plot charts
plot_price_chart(data, crypto, sma_period)
plot_rsi_chart(data)
plot_macd_chart(data)