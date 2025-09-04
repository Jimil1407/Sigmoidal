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
    <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
            <div>
                <h1 className="text-2xl font-semibold">Dashboard</h1>
                <p className="text-sm text-white/60 mt-1">Overview of your portfolio and live market data.</p>
            </div>
            <button onClick={() => fetchData()} className="px-4 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Refresh</button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                <div className="text-xs text-white/60">Portfolio</div>
                <div className="mt-1 text-lg font-semibold">{portfolio?.name ?? "-"}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                <div className="text-xs text-white/60">Total Value</div>
                <div className="mt-1 text-lg font-semibold">{portfolio?.totalValue ?? "-"}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                <div className="text-xs text-white/60">Cash</div>
                <div className="mt-1 text-lg font-semibold">{portfolio?.cash ?? "-"}</div>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
                <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold">Positions</h2>
                        <span className="text-xs text-white/60">{positions?.length ?? 0} items</span>
                    </div>
                    <div className="space-y-3">
                        {positions?.length ? positions.map((p) => (
                            <div key={p.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-[#0B0C14] px-4 py-3">
                                <div className="text-sm">#{p.stockId}</div>
                                <div className="text-sm text-white/70">Qty {p.quantity}</div>
                                <div className="text-sm font-medium">@ {p.avgPrice}</div>
                            </div>
                        )) : (
                            <div className="text-sm text-white/60">No positions yet.</div>
                        )}
                    </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold">Trades</h2>
                        <span className="text-xs text-white/60">{trades?.length ?? 0} items</span>
                    </div>
                    <div className="space-y-3">
                        {trades?.length ? trades.map((t) => (
                            <div key={t.id} className="grid grid-cols-4 gap-3 items-center rounded-xl border border-white/10 bg-[#0B0C14] px-4 py-3">
                                <div className="text-sm">{t.tradeType}</div>
                                <div className="text-sm text-white/70">#{t.stockId}</div>
                                <div className="text-sm">Qty {t.quantity}</div>
                                <div className="text-sm font-medium">@ {t.price}</div>
                            </div>
                        )) : (
                            <div className="text-sm text-white/60">No trades yet.</div>
                        )}
                    </div>
                </div>
            </div>

            <div className="space-y-6">
                <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                    <h2 className="text-lg font-semibold mb-4">Place Order</h2>
                    <form onSubmit={handleSubmitTrade} className="space-y-3">
                        <input className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" type="text" name="stockId" placeholder="Stock ID" />
                        <div className="grid grid-cols-2 gap-3">
                            <input className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" type="text" name="quantity" placeholder="Quantity" />
                            <input className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" type="text" name="price" placeholder="Price" />
                        </div>
                        <button type="submit" className="w-full px-4 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Buy</button>
                    </form>
                </div>

                <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
                    <h2 className="text-lg font-semibold mb-4">Live Market</h2>
                    <form onSubmit={(e) => {
                        e.preventDefault();
                        const form = e.target as HTMLFormElement;
                        const symbol = (form.symbol as HTMLInputElement).value;
                        if (!symbol || !socket) return;
                        setLiveSymbol(symbol.toUpperCase());
                        socket.send(JSON.stringify({ type: "subscribe", symbol }));
                    }} className="flex items-center gap-2">
                        <input className="flex-1 rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" type="text" name="symbol" placeholder="Symbol (e.g. AAPL)" />
                        <button type="submit" disabled={!socket} className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 font-semibold disabled:opacity-60">Subscribe</button>
                    </form>
                    <button className="mt-3 w-full px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 font-semibold disabled:opacity-60" disabled={!socket || !liveSymbol} onClick={() => {
                        if (!socket || !liveSymbol) return;
                        socket.send(JSON.stringify({ type: "unsubscribe", symbol: liveSymbol }));
                    }}>Unsubscribe</button>
                    <div className="mt-3 text-sm text-white/70">Live {liveSymbol ? `${liveSymbol}: ${livePrice ?? "-"}` : "-"}</div>
                </div>
            </div>
        </div>
    </div>
  );
}