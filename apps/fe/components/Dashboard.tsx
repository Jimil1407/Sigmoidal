"use client";
import { useEffect, useState } from "react";
import axios from "axios";

export default function Dashboard() {

    type Portfolio = {
        id: number;
        name: string;
        totalValue: number;
        cash: number;
    }
    type Position = {
        id: number;
        portfolioId: number;
        stockId: number;
        quantity: number;
        avgPrice: number;
    }
    type Trade = {
        id: number;
        portfolioId: number;
        stockId: number;
        tradeType: string;
        quantity: number;
        price: number;
    }
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const [positions, setPositions] = useState<Position[] | null>(null);
    const [trades, setTrades] = useState<Trade[] | null>(null);
    const fetchData = async () => {
            const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
            if (!token) return;
            const authHeader = { Authorization: token } as const;
            const response = await axios.get(`http://localhost:8080/api/v1/portfolio/myportfolio`, { headers: authHeader });
            setPortfolio(response.data);
            const positionsResponse = await axios.get(`http://localhost:8080/api/v1/portfolio/myportfolio/positions`, { headers: authHeader });
            setPositions(positionsResponse.data);
            const tradesResponse = await axios.get(`http://localhost:8080/api/v1/portfolio/myportfolio/trades`, { headers: authHeader });
            setTrades(tradesResponse.data);
    };
    useEffect(() => {
        fetchData();
    }, []);
    
  return (
    <div>
        <button onClick={() => {
            fetchData();
        }}>Fetch Portfolio</button>
      <h1>Dashboard</h1>
      <h2>Portfolio: {portfolio?.name}</h2>
      <h2>Value: {portfolio?.totalValue}</h2>
      <h2>Cash: {portfolio?.cash}</h2>
      <h2>Positions: {positions?.length}</h2>
      <h2>Trades: {trades?.length}</h2>
    </div>
  );
}