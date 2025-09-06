"use client";
import axios from "axios";
import { useState } from "react";

export default function PredictValue() {
  const [symbol, setSymbol] = useState("");
  const [prediction, setPrediction] = useState("");

  const predictValue = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8080/api/v1/predictions/predict/${symbol}`
      );
      setPrediction(response.data.prediction);
    } catch (error) {
      setPrediction("Error fetching prediction");
    }
  };

  return (
    <div className=" flex items-center justify-center bg-[#0B0C14] px-4">
      <div className="w-full max-w-md p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-lg shadow-lg">
        <h1 className="text-2xl font-semibold text-white mb-6 text-center">
          Stock Value Predictor
        </h1>

        <div className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Enter stock symbol"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="w-full p-3 rounded-xl bg-white/10 text-white placeholder-gray-400 border border-white/10 focus:outline-none focus:ring-2 focus:ring-[#7B6CF6] transition"
          />

          <button
            onClick={predictValue}
            className="w-full py-3 rounded-xl font-medium text-white bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] hover:opacity-90 transition-all duration-300 shadow-md"
          >
            Predict
          </button>
        </div>

        {prediction && (
          <div className="mt-6 p-4 rounded-xl bg-white/10 border border-white/10 text-center">
            <p className="text-lg text-white">
              $
              {!isNaN(Number(prediction))
                ? Number(prediction).toFixed(2)
                : prediction}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
