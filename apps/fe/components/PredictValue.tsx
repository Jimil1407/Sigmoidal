"use client";
import axios from "axios";
import { useState } from "react";

export default function PredictValue() {
    const [symbol, setSymbol] = useState("");
    const [prediction, setPrediction] = useState("");

    const predictValue = async () => {
        const response = await axios.get(`http://localhost:8080/api/v1/predictions/predict/${symbol}`);
        setPrediction("Predicted value: " + response.data.prediction);
    }

    return (
        <div>
            <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
            <button onClick={predictValue}>Predict</button>
            <p>{prediction}</p>
        </div>
    )
}