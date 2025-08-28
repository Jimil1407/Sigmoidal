from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
import numpy as np

def predict(X_test, df, model_path: str):

    # Fit a scaler on historical Close prices to invert the target scaling
    scaler = MinMaxScaler(feature_range=(0, 1))
    close_values = df['Close'].values[1:].reshape(-1, 1)
    scaler.fit(close_values)

    try:
        model = keras.models.load_model(model_path)
    except Exception as exc:
        print(f"Error loading model from {model_path}: {exc}")
        return 500

    if model is not None:
        if len(X_test) > 0:
            last_sequence = X_test[-1]
            last_sequence = last_sequence.reshape(1, last_sequence.shape[0], last_sequence.shape[1])
            predicted_scaled_price = model.predict(last_sequence)
            predicted_price = scaler.inverse_transform(predicted_scaled_price)[:, 0]
            print(f"Predicted next closing price (scaled): {predicted_scaled_price}")
            print(f"Predicted next closing price (actual): {predicted_price[0]}")

            return predicted_price[0]
        else:
            print("No test data available to simulate prediction.")
            return 500
    else:
        print("Model not loaded, cannot make predictions.")
        return 500