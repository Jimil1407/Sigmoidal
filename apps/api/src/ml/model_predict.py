import os
import asyncio
import httpx
import pandas as pd
import numpy as np
import ta
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

import snscrape.modules.twitter as sntwitter

tweets = []
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'${symbol} since:{start_date} until:{end_date}').get_items()):
    if i > max_tweets_per_day:  # control tweet load
        break
    tweets.append({
        'date': tweet.date,
        'content': tweet.content,
        'retweetCount': tweet.retweetCount,
    })

print(tweets)


# Directory setup
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
SCALERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scalers"))
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SCALERS_DIR, exist_ok=True)

# 1. Fetch Data
async def get_data(symbol: str, period="1y", interval="1d") -> pd.DataFrame:
    url = f"http://localhost:8080/api/v1/market/history/{symbol}"
    params = {"period": period, "interval": interval}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
    return df

# 2. Feature Engineering & Preprocessing
def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure datetime index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    # Technical Indicators
    df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
    df['BB_High'], df['BB_Low'] = (
        ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2).bollinger_hband(),
        ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2).bollinger_lband()
    )
    df.dropna(inplace=True)
    return df

def preprocess(df: pd.DataFrame, seq_len=60):
    df = add_technical_indicators(df)
    # Features and target
    feature_cols = ['Open','High','Low','Close','Volume','RSI_14','SMA_20','BB_High','BB_Low']
    data = df[feature_cols].values
    target = df['Close'].values.reshape(-1,1)
    # Scale features and target separately
    feat_scaler = MinMaxScaler()
    tgt_scaler  = MinMaxScaler()
    data_scaled   = feat_scaler.fit_transform(data)
    target_scaled = tgt_scaler.fit_transform(target)
    # Save scalers
    joblib.dump(feat_scaler, os.path.join(SCALERS_DIR, 'feat_scaler.gz'))
    joblib.dump(tgt_scaler,  os.path.join(SCALERS_DIR, 'tgt_scaler.gz'))
    # Build sequences
    X, y = [], []
    for i in range(len(data_scaled) - seq_len):
        X.append(data_scaled[i:i+seq_len])
        y.append(target_scaled[i+seq_len])
    X, y = np.array(X), np.array(y)
    # Time-series split
    split_index = int(0.8 * len(X))
    return X[:split_index], X[split_index:], y[:split_index], y[split_index:]

# 3. Model Creation & Training
def build_model(input_shape):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(64),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='huber')
    return model

def train_model(X_train, y_train, X_val, y_val, symbol):
    model = build_model(X_train.shape[1:])
    # Callbacks
    chkpt_path = os.path.join(MODELS_DIR, f"{symbol}_best.keras")
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ModelCheckpoint(chkpt_path, save_best_only=True, monitor='val_loss')
    ]
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )
    # Save final model
    final_path = os.path.join(MODELS_DIR, f"{symbol}.keras")
    model.save(final_path, include_optimizer=False)
    return final_path, chkpt_path

# 4. Evaluation & Prediction
def evaluate_and_predict(model_path, X_test, symbol):
    # Load best model
    model = load_model(model_path)
    # Load target scaler
    tgt_scaler = joblib.load(os.path.join(SCALERS_DIR, 'tgt_scaler.gz'))
    # Predict next step from last sequence
    last_seq = X_test[-1][None, ...]
    pred_scaled = model.predict(last_seq)
    pred_price  = tgt_scaler.inverse_transform(pred_scaled)[0,0]
    print(f"Next-day predicted close price for {symbol}: {pred_price:.2f}")
    return pred_price

# 5. Orchestrator
async def predict_stock(symbol: str):
    df = await get_data(symbol)
    X_train,X_test,y_train,y_test = preprocess(df)
    final_model, best_model = train_model(X_train, y_train, X_test, y_test, symbol)
    return evaluate_and_predict(best_model, X_test, symbol)

if __name__ == "__main__":
    symbol = input("Enter stock symbol: ").strip().upper()
    price = asyncio.run(predict_stock(symbol))
