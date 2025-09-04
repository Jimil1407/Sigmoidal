"use client";
import { useEffect, useState } from "react";
import axios from "axios";

export type Portfolio = {
    id: number;
    name: string;
    totalValue: number;
    cash: number;
};
export type Position = {
    id: number;
    portfolioId: number;
    stockId: number;
    quantity: number;
    avgPrice: number;
};
export type Trade = {
    id: number;
    portfolioId: number;
    stockId: number;
    tradeType: string;
    quantity: number;
    price: number;
};

export default function PortfolioInfo() {
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const [positions, setPositions] = useState<Position[] | null>(null);
    const [trades, setTrades] = useState<Trade[] | null>(null);

    const fetchData = async () => {
        const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
        if (!token) return;
        const authHeader = { Authorization: token } as const;
        const response = await axios.get(`http://localhost:8080/api/v1/portfolio/myportfolio`, { headers: authHeader });
        setPortfolio(response.data as Portfolio);
        const positionsResponse = await axios.get(`http://localhost:8080/api/v1/portfolio/myportfolio/positions`, { headers: authHeader });
        setPositions(positionsResponse.data as Position[]);
        const tradesResponse = await axios.get(`http://localhost:8080/api/v1/portfolio/myportfolio/trades`, { headers: authHeader });
        setTrades(tradesResponse.data as Trade[]);
    };

    useEffect(() => {
        fetchData();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold">Dashboard</h1>
                    <p className="text-sm text-white/60 mt-1">Overview of your portfolio and live market data.</p>
                </div>
                <button onClick={() => fetchData()} className="px-4 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Refresh</button>
            </div>

            <section id="portfolio" className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
            </section>

            <section id="positions" className="space-y-6">
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

                <div id="trades" className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
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
            </section>
        </div>
    );
}