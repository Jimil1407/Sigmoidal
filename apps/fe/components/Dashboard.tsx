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
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [livePrice, setLivePrice] = useState<number | null>(null);
    const [liveSymbol, setLiveSymbol] = useState<string>("");
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

    useEffect(() => {
        const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
        if (!token) return;
        const ws = new WebSocket(`ws://localhost:8080/ws/getlivedata?token=${encodeURIComponent(token)}`);
        ws.onopen = () => {
            setSocket(ws);
        };
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data && data.type === "market_data") {
                    setLiveSymbol(data.symbol);
                    setLivePrice(data.price);
                }
            } catch {}
        };
        ws.onclose = () => {
            setSocket(null);
        };
        return () => {
            ws.close();
        };
    }, []);

    const handleSubmitTrade = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
        if (!token) return;
        const authHeader = { Authorization: token } as const;
        const stockId = (e.target as HTMLFormElement).stockId.value;
        const quantity = (e.target as HTMLFormElement).quantity.value;
        const price = (e.target as HTMLFormElement).price.value;
        const response = await axios.post(`http://localhost:8080/api/v1/portfolio/myportfolio/trade`, { stockId, quantity, price }, { headers: authHeader });
        fetchData();
    };
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

      <div style={{ marginTop: 16 }}>
        <form onSubmit={(e) => {
          e.preventDefault();
          const form = e.target as HTMLFormElement;
          const symbol = (form.symbol as HTMLInputElement).value;
          if (!symbol || !socket) return;
          socket.send(JSON.stringify({ type: "subscribe", symbol }));
        }}>
          <input type="text" name="symbol" placeholder="Symbol (e.g. AAPL)" />
          <button type="submit" disabled={!socket}>Subscribe</button>
        </form>
        <button style={{ marginTop: 8 }} disabled={!socket || !liveSymbol} onClick={() => {
          if (!socket || !liveSymbol) return;
          socket.send(JSON.stringify({ type: "unsubscribe", symbol: liveSymbol }));
        }}>Unsubscribe</button>
        <div style={{ marginTop: 8 }}>
          Live {liveSymbol ? `${liveSymbol}: ${livePrice ?? "-"}` : "-"}
        </div>
      </div>
    </div>
  );
}