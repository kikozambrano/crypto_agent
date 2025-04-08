import os
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import ta

# 📥 Fetch data
def get_crypto_data(ticker, start="2020-01-01"):
    data = yf.download(ticker, start=start, interval="1d")
    return data

# 📈 Add indicators
def add_indicators(df):
    df = df.copy()

    # Ensure 'Close' is a flat Series
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    df['SMA_50'] = ta.trend.sma_indicator(close, window=50)
    df['RSI'] = ta.momentum.rsi(close, window=14)
    macd_indicator = ta.trend.MACD(close)
    df['MACD'] = macd_indicator.macd_diff()

    return df

# 🪙 Define cryptos
cryptos = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana"
}

# 🔁 Loop through each and plot
for ticker, name in cryptos.items():
    df = get_crypto_data(ticker)

    if df.empty:
        print(f"❌ {name} data not loaded.")
        continue

    df = add_indicators(df)

    print(f"\n✅ {name} Data:")
    print(df[['Close', 'Volume', 'SMA_50', 'RSI', 'MACD']].tail())

    # 📊 Price + SMA
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_title(f"{name} Price and Volume")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price (USD)", color='blue')
    ax1.plot(df['Close'], label='Close Price', color='blue')
    ax1.plot(df['SMA_50'], label='SMA 50', color='black')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.legend(loc='upper left')
    ax1.grid()

    volume = pd.to_numeric(df['Volume'].values.flatten(), errors='coerce')
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel("Volume", color='gray')
    ax2.bar(df.index, volume, alpha=0.3, color='gray', label='Volume')
    ax2.tick_params(axis='y', labelcolor='gray')

    fig.tight_layout()
    # plt.show()

    # 🧠 RSI
    # plt.figure(figsize=(12, 4))
    # plt.plot(df['RSI'], label='RSI', color='orange')
    # plt.axhline(70, color='red', linestyle='--')
    # plt.axhline(30, color='green', linestyle='--')
    # plt.title(f"{name} RSI")
    # plt.xlabel("Date")
    # plt.ylabel("RSI Value")
    # plt.grid()
    # plt.show()

    # 🔁 MACD
    # plt.figure(figsize=(12, 4))
    # plt.plot(df['MACD'], label='MACD Histogram', color='purple')
    # plt.axhline(0, color='gray', linestyle='--')
    # plt.title(f"{name} MACD Histogram")
    # plt.xlabel("Date")
    # plt.ylabel("MACD Value")
    # plt.grid()
    # plt.show()


    # 📁 Save to Excel-compatible CSV
    output_dir = "crypto_data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{ticker.replace('-USD', '')}_data.csv")
    df.to_csv(output_path)
    print(f"📦 Saved {name} data to {output_path}")