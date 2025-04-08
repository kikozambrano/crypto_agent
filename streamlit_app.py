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

data["SMA"] = ta.trend.sma_indicator(close, window=sma_period)
data["RSI"] = ta.momentum.rsi(close, window=rsi_period)
macd = ta.trend.MACD(close, window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_signal)
data["MACD"] = macd.macd_diff()
data["MACD_line"] = macd.macd()
data["MACD_signal"] = macd.macd_signal()

# Labeling function
def label_data(df, holding_period, buy_threshold, sell_threshold):
    df = df.copy()

    # Create future close column and ensure alignment
    future_close = df["Close"].shift(-holding_period)
    future_return = ((future_close - df["Close"]) / df["Close"]).astype(float)
    df["Future_Return"] = pd.Series(future_return.values, index=df.index)
    
    # Drop rows with NaNs to avoid index misalignment
    df = df.dropna(subset=["Future_Return"])

    # Initialize signal column
    df["Signal"] = 0
    df.loc[df["Future_Return"] >= buy_threshold / 100, "Signal"] = 1
    df.loc[df["Future_Return"] <= -sell_threshold / 100, "Signal"] = -1

    return df

# Apply labeling
data = label_data(data, holding_period, buy_threshold, sell_threshold)

# Optional: show raw data
if st.checkbox("Show raw data"):
    st.dataframe(data.tail(20))

# Price Chart with Indicators + Signals
st.subheader(f"{crypto} Price and Indicators")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data.index, data["Close"], label="Close Price", color='blue')
ax.plot(data.index, data["SMA"], label=f"SMA {sma_period}", color='black')
ax.set_ylabel("Price (USD)")
ax.set_xlabel("Date")
ax.grid()

# Add BUY/SELL markers
buy_signals = data[data["Signal"] == 1]
sell_signals = data[data["Signal"] == -1]
ax.scatter(buy_signals.index, buy_signals["Close"], label="BUY", marker="^", color="green", s=100)
ax.scatter(sell_signals.index, sell_signals["Close"], label="SELL", marker="v", color="red", s=100)
ax.legend()

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

# Download labeled data (optional future step)
# st.download_button("Download CSV", data.to_csv(index=True), "crypto_data.csv")