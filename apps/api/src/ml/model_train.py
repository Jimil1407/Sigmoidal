import httpx
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os
import pickle
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error

directory = "../models"
os.makedirs(directory, exist_ok=True)


def get_data(symbol: str):
    params = {
        "period": "9mo",
        "interval": "1d"
    }
    response = httpx.get(
        f"http://localhost:8080/api/v1/market/history/{symbol}",
        params=params
    )
    try:
        # If API returns JSON array of records
        df = pd.DataFrame(response.json())
        print(df.head())
        print(df.info())
    except FileNotFoundError:
        print("Error: temo.json not found. Please make sure the file is in the correct directory.")
        df = None
    return df

def preprocess(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df.fillna(df.mean(numeric_only=True), inplace=True)

    features = ['Open', 'High', 'Low', 'Close', 'Volume']
    data = df[features].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    target = df['Close'].shift(-1).values

    target = target[:-1]
    scaled_data = scaled_data[:-1]

    sequence_length = 12
    X,y = [] , []

    for i in range(len(scaled_data) - sequence_length):
        X.append(scaled_data[i:(i+sequence_length),:])
        y.append(target[i + sequence_length])

    X = np.array(X)
    y = np.array(y)

    y = y.reshape(-1,1)
    y = scaler.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    print("Data cleaning and preparation complete.")
    print(f"Shape of X_train: {X_train.shape}")
    print(f"Shape of y_train: {y_train.shape}")
    print(f"Shape of X_test: {X_test.shape}")
    print(f"Shape of y_test: {y_test.shape}")

    return X_train, X_test, y_train, y_test

def model_train(X_train, X_test, y_train, y_test, stock: str):
    model = Sequential()


    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))

    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))
    model_filename = f"{directory}/{stock}.pkl"
    with open(model_filename, "wb") as f:
        pickle.dump(model, f)

    print(f"Model training complete. Model saved at models/{stock}.pkl")


def evaluate(X_test, y_test, stock: str):
    model_filename = "../models/f'{stock}.pkl'"
    with open(model_filename, "rb") as f:
        model = pickle.load(f)

    mse = model.evaluate(X_test, y_test, verbose=0)
    rmse = np.sqrt(mse)

    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")

def predict(X_test, df):

    scaler = MinMaxScaler(feature_range=(0, 1))
    features = ['Open', 'High', 'Low', 'Close', 'Volume']
    data = df[features].values

    model_filename = "../models/f'{stock}.pkl'"
    with open(model_filename, "rb") as f:
        model = pickle.load(f)

    if model is not None:
        if len(X_test) > 0:
            last_sequence = X_test[-1]
            last_sequence = last_sequence.reshape(1, last_sequence.shape[0], last_sequence.shape[1])
            predicted_scaled_price = model.predict(last_sequence)
            dummy_array = np.zeros((predicted_scaled_price.shape[0], data.shape[1]))
            dummy_array[:, 3] = predicted_scaled_price[:, 0]
            predicted_price = scaler.inverse_transform(dummy_array)[:, 3]
            print(f"Predicted next closing price (scaled): {predicted_scaled_price}")
            print(f"Predicted next closing price (actual): {predicted_price[0]}")
        else:
            print("No test data available to simulate prediction.")
    else:
        print("Model not loaded, cannot make predictions.")



if __name__ == "__main__":
    stock = input("Enter the stock symbol")
    df = get_data(stock)
    X_train, X_test, y_train, y_test = preprocess(df)
    model_train(X_train, X_test, y_train, y_test,stock)
    evaluate(X_test, y_test, stock)
    predict(X_test, df)

