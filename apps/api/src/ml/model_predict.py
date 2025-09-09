import os
import asyncio
import pandas as pd
import numpy as np
import ta
import shutil
import joblib
from datetime import datetime, timedelta

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Directory setup
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
SCALERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scalers"))
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SCALERS_DIR, exist_ok=True)

## Sentiment analysis removed

# ---- STOCK DATA FETCHING ----

import httpx
async def get_data(symbol: str, period="1y", interval="1d") -> pd.DataFrame:
    url = f"http://localhost:8080/api/v1/market/history/{symbol}"
    params = {"period": period, "interval": interval}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
    return df

# ---- FEATURE ENGINEERING ----

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low'] = bb.bollinger_lband()
    df.dropna(inplace=True)
    print(df.head())
    return df

def preprocess(df: pd.DataFrame, seq_len=60):
    df = add_technical_indicators(df)
    feature_cols = ['Open','High','Low','Close','Volume','RSI_14','SMA_20','BB_High','BB_Low']
    data = df[feature_cols].values
    target = df['Close'].values.reshape(-1,1)
    feat_scaler = MinMaxScaler()
    tgt_scaler  = MinMaxScaler()
    data_scaled   = feat_scaler.fit_transform(data)
    target_scaled = tgt_scaler.fit_transform(target)
    joblib.dump(feat_scaler, os.path.join(SCALERS_DIR, 'feat_scaler.gz'))
    joblib.dump(tgt_scaler,  os.path.join(SCALERS_DIR, 'tgt_scaler.gz'))
    X, y = [], []
    for i in range(len(data_scaled) - seq_len):
        X.append(data_scaled[i:i+seq_len])
        y.append(target_scaled[i+seq_len])
    X, y = np.array(X), np.array(y)
    split_index = int(0.8 * len(X))
    return X[:split_index], X[split_index:], y[:split_index], y[split_index:]

# ---- MODEL ----

def build_model(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(64),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='huber')
    return model

def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d%H%M%S')

def _version_artifacts(symbol: str, base_model_path: str):
    ts = _timestamp()
    # Model versions
    ts_model = os.path.join(MODELS_DIR, f"{symbol}-{ts}.keras")
    latest_model = os.path.join(MODELS_DIR, f"{symbol}_latest.keras")
    shutil.copyfile(base_model_path, ts_model)
    shutil.copyfile(base_model_path, latest_model)
    # Scaler versions
    feat_src = os.path.join(SCALERS_DIR, 'feat_scaler.gz')
    tgt_src  = os.path.join(SCALERS_DIR, 'tgt_scaler.gz')
    feat_ts = os.path.join(SCALERS_DIR, f"feat_scaler-{symbol}-{ts}.gz")
    tgt_ts  = os.path.join(SCALERS_DIR, f"tgt_scaler-{symbol}-{ts}.gz")
    feat_latest = os.path.join(SCALERS_DIR, f"feat_scaler-{symbol}_latest.gz")
    tgt_latest  = os.path.join(SCALERS_DIR, f"tgt_scaler-{symbol}_latest.gz")
    if os.path.exists(feat_src):
        shutil.copyfile(feat_src, feat_ts)
        shutil.copyfile(feat_src, feat_latest)
    if os.path.exists(tgt_src):
        shutil.copyfile(tgt_src, tgt_ts)
        shutil.copyfile(tgt_src, tgt_latest)
    return {
        'model_ts': ts_model,
        'model_latest': latest_model,
        'feat_scaler_ts': feat_ts,
        'feat_scaler_latest': feat_latest,
        'tgt_scaler_ts': tgt_ts,
        'tgt_scaler_latest': tgt_latest,
    }

def _latest_artifacts(symbol: str):
    return {
        'model': os.path.join(MODELS_DIR, f"{symbol}_latest.keras"),
        'feat_scaler': os.path.join(SCALERS_DIR, f"feat_scaler-{symbol}_latest.gz"),
        'tgt_scaler': os.path.join(SCALERS_DIR, f"tgt_scaler-{symbol}_latest.gz"),
    }

def train_model(X_train, y_train, X_val, y_val, symbol):
    model = build_model(X_train.shape[1:])
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
    final_path = os.path.join(MODELS_DIR, f"{symbol}.keras")
    model.save(final_path, include_optimizer=False)
    versions = _version_artifacts(symbol, chkpt_path if os.path.exists(chkpt_path) else final_path)
    return versions['model_latest'], versions['model_ts']

def evaluate_and_predict(model_path, X_test, symbol):
    model = load_model(model_path)
    tgt_scaler = joblib.load(os.path.join(SCALERS_DIR, 'tgt_scaler.gz'))
    last_seq = X_test[-1][None, ...]
    pred_scaled = model.predict(last_seq)
    pred_price  = tgt_scaler.inverse_transform(pred_scaled)[0,0]
    print(f"Next-day predicted close price for {symbol}: {pred_price:.2f}")
    return pred_price

# ---- PREDICT-ONLY (no retrain) ----

def _build_features_only(df: pd.DataFrame) -> pd.DataFrame:
    df = add_technical_indicators(df)
    return df[['Open','High','Low','Close','Volume','RSI_14','SMA_20','BB_High','BB_Low']]

async def predict_only(symbol: str, seq_len: int = 60):
    artifacts = _latest_artifacts(symbol)
    model_path = artifacts['model']
    feat_scaler_path = artifacts['feat_scaler']
    tgt_scaler_path  = artifacts['tgt_scaler']
    if not (os.path.exists(model_path) and os.path.exists(feat_scaler_path) and os.path.exists(tgt_scaler_path)):
        raise FileNotFoundError("Latest artifacts not found. Train the model first.")

    df = await get_data(symbol)
    feat_df = _build_features_only(df)
    if len(feat_df) < seq_len + 1:
        raise ValueError("Not enough data for prediction window.")

    feat_scaler = joblib.load(feat_scaler_path)
    tgt_scaler  = joblib.load(tgt_scaler_path)

    data_scaled = feat_scaler.transform(feat_df.values)
    X = []
    for i in range(len(data_scaled) - seq_len):
        X.append(data_scaled[i:i+seq_len])
    X = np.array(X)
    model = load_model(model_path)
    last_seq = X[-1][None, ...]
    pred_scaled = model.predict(last_seq)
    pred_price  = tgt_scaler.inverse_transform(pred_scaled)[0,0]
    print(f"Next-day predicted close price (no retrain) for {symbol}: {pred_price:.2f}")
    return pred_price

# ---- END-TO-END ORCHESTRATOR ----

async def predict_stock(symbol: str):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=370)
    df = await get_data(symbol)
    X_train, X_test, y_train, y_test = preprocess(df)
    final_model, best_model = train_model(X_train, y_train, X_test, y_test, symbol)
    return evaluate_and_predict(best_model, X_test, symbol)

if __name__ == "__main__":
    symbol = input("Enter stock symbol: ").strip().upper()
    price = asyncio.run(predict_stock(symbol))
