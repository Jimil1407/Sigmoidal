from sklearn.preprocessing import MinMaxScaler
import pickle

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

            return predicted_price[0]
        else:
            print("No test data available to simulate prediction.")
            return 500
    else:
        print("Model not loaded, cannot make predictions.")
        return 500