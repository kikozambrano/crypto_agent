import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

# App title
st.title("📊 Crypto Indicator Dashboard")

# Sidebar inputs
st.sidebar.header("Settings")

crypto = st.sidebar.selectbox("Select a cryptocurrency", ["BTC-USD", "ETH-USD", "SOL-USD"])
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))

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

# Download historical data
data = yf.download(crypto, start=start_date, interval="1d")

if data.empty:
    st.error("Failed to load data. Please check your internet connection or symbol.")
    st.stop()

# Add indicators
close = data["Close"]
if isinstance(close, pd.DataFrame):
    close = close.squeeze()

data["SMA"] = ta.trend.sma_indicator(close, window=sma_period)
data["RSI"] = ta.momentum.rsi(close, window=rsi_period)
macd = ta.trend.MACD(close, window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_signal)
data["MACD"] = macd.macd_diff()
data["MACD_line"] = macd.macd()
data["MACD_signal"] = macd.macd_signal()

# Show data table (optional)
if st.checkbox("Show raw data"):
    st.dataframe(data.tail(20))

# Plotting
st.subheader(f"{crypto} Price and Indicators")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data.index, data["Close"], label="Close Price", color='blue')
ax.plot(data.index, data["SMA"], label=f"SMA {sma_period}", color='black')
ax.set_ylabel("Price (USD)")
ax.set_xlabel("Date")
ax.legend()
ax.grid()
st.pyplot(fig)

# RSI Plot
st.subheader("RSI")
fig_rsi, ax_rsi = plt.subplots(figsize=(12, 2))
ax_rsi.plot(data.index, data["RSI"], label="RSI", color='orange')
ax_rsi.axhline(70, color='red', linestyle='--')
ax_rsi.axhline(30, color='green', linestyle='--')
ax_rsi.set_ylabel("RSI")
ax_rsi.grid()
st.pyplot(fig_rsi)

# MACD Plot
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

# Download labeled data (future step)
# st.download_button("Download CSV", data.to_csv(index=True), "crypto_data.csv")