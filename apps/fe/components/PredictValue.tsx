"use client";
import axios from "axios";
import { useState, useEffect } from "react";
import { toast } from "react-toastify";

export default function PredictValue() {
  const [symbol, setSymbol] = useState("");
  const [prediction, setPrediction] = useState("");
  const [status, setStatus] = useState("");
  const [isTraining, setIsTraining] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);

  // Clear prediction when symbol changes
  useEffect(() => {
    setPrediction("");
  }, [symbol]);
  const predictValue = async () => {
    if (!symbol.trim()) {
      toast.error("Please enter a stock symbol");
      return;
    }
    
    setIsPredicting(true);
    setPrediction("");
    setStatus("Making prediction...");
    
    try {
      const response = await axios.get(
        `https://sigmoidal-backend.onrender.com/api/v1/predictions/predict/${symbol}`
      );
      setPrediction(response.data.prediction);
      setStatus("Prediction completed successfully");
      toast.success("Prediction completed successfully");
    } catch {
      setPrediction("Error fetching prediction");
      setStatus("Error occurred during prediction");
      toast.error("Error fetching prediction");
    } finally {
      setIsPredicting(false);
    }
  };

  const trainModel = async () => {
    if (!symbol.trim()) {
      toast.error("Please enter a stock symbol");
      return;
    }
    
    setIsTraining(true);
    setStatus("Training model... This may take a few minutes");
    
    try {
      await axios.get(
        `https://sigmoidal-backend.onrender.com/api/v1/predictions/train/${symbol}`,
        { timeout: 300000 } // 5 minutes timeout for training
      );
      setStatus("Model trained successfully");
      toast.success("Model trained successfully");
    } catch (error) {
      console.error(error);
      setStatus("Error occurred during training");
      toast.error("Error training model");
    } finally {
      setIsTraining(false);
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
            placeholder="Enter stock symbol (e.g., AAPL, TSLA)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            disabled={isTraining || isPredicting}
            className="w-full p-3 rounded-xl bg-white/10 text-white placeholder-gray-400 border border-white/10 focus:outline-none focus:ring-2 focus:ring-[#7B6CF6] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          
          <button 
            onClick={trainModel}
            disabled={isTraining || isPredicting}
            className="w-full py-3 rounded-xl font-medium text-white bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] hover:opacity-90 active:scale-95 transition-all duration-200 shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100 flex items-center justify-center gap-2"
          >
            {isTraining ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Training Model...
              </>
            ) : (
              "Train Model"
            )}
          </button>
          
          {status && (
            <div className="p-3 rounded-xl bg-white/5 border border-white/10">
              <p className="text-sm text-white/80">{status}</p>
            </div>
          )}
          
          <button
            onClick={predictValue}
            disabled={isTraining || isPredicting}
            className="w-full py-3 rounded-xl font-medium text-white bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] hover:opacity-90 active:scale-95 transition-all duration-200 shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100 flex items-center justify-center gap-2"
          >
            {isPredicting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Predicting...
              </>
            ) : (
              "Predict Price"
            )}
          </button>
        </div>

        {prediction && !isPredicting && (
          <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 text-center">
            <p className="text-lg text-white font-semibold">
              Predicted Price for {symbol}: $
              {!isNaN(Number(prediction))
                ? Number(prediction).toFixed(2)
                : prediction}
            </p>
            <p className="text-sm text-white/60 mt-1">
              Based on 1 year of historical data
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
