"use client";
import { useState, useEffect, useRef } from "react";
import MarketCard from "./MarketCard";

type MarketData = {
    symbol: string;
    current: number;
    high: number;
    low: number;
    change: number;
    percent_change: number;
};

export default function LiveData() {
    const [symbols, setSymbols] = useState<string[]>([]);
    const [inputSymbol, setInputSymbol] = useState("");
    const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
    const [, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    // WebSocket connection management
    useEffect(() => {
        const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
        if (!token) return;

        const protocol = typeof window !== "undefined" && window.location.protocol === "https:" ? "wss" : "ws";
        const host = process.env.NEXT_PUBLIC_API_HOST ?? "sigmoidal-backend.onrender.com";
        const ws = new WebSocket(`${protocol}://${host}/ws/getlivedata?token=${encodeURIComponent(token)}`);
        wsRef.current = ws;

        ws.onopen = () => {
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                
                if (message.type === "market_data") {
                    setMarketData(prev => ({
                        ...prev,
                        [message.symbol]: {
                            symbol: message.symbol,
                            current: message.current,
                            high: message.high,
                            low: message.low,
                            change: message.change,
                            percent_change: message.percent_change,
                            lastUpdated: Date.now()
                        }
                    }));
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        ws.onerror = () => {
            setIsConnected(false);
        };

        ws.onclose = () => {
            setIsConnected(false);
        };

        return () => {
            ws.close();
        };
    }, []);

    const addSymbol = (symbol: string) => {
        const upperSymbol = symbol.toUpperCase().trim();
        if (upperSymbol && !symbols.includes(upperSymbol)) {
            setSymbols([...symbols, upperSymbol]);
            setInputSymbol("");
            
            // Subscribe to the symbol via WebSocket
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ type: "subscribe", symbol: upperSymbol }));
            }
        }
    };

    const removeSymbol = (symbolToRemove: string) => {
        setSymbols(symbols.filter(s => s !== symbolToRemove));
        
        // Unsubscribe from the symbol via WebSocket
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: "unsubscribe", symbol: symbolToRemove }));
        }
        
        // Remove data for this symbol
        setMarketData(prev => {
            const newData = { ...prev };
            delete newData[symbolToRemove];
            return newData;
        });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        addSymbol(inputSymbol);
    };

    return (
        <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Live Market</h2>
                <div className="text-xs text-white/60">
                    {symbols.length} active
                </div>
            </div>

            {/* Add Symbol Form */}
            <form onSubmit={handleSubmit} className="flex items-center gap-2 mb-4">
                <input 
                    className="flex-1 rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" 
                    type="text" 
                    placeholder="Symbol (e.g. AAPL)" 
                    value={inputSymbol}
                    onChange={(e) => setInputSymbol(e.target.value)}
                />
                <button 
                    type="submit" 
                    className="px-4 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold transition-colors"
                >
                    Add
                </button>
            </form>

            {/* Market Cards */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
                {symbols.length === 0 ? (
                    <div className="text-center py-8 text-white/50 text-sm">
                        Add a stock symbol to see live market data
                    </div>
                ) : (
                    symbols.map((symbol) => (
                        <MarketCard 
                            key={symbol} 
                            symbol={symbol} 
                            onRemove={() => removeSymbol(symbol)}
                            data={marketData[symbol] || null}
                        />
                    ))
                )}
            </div>

            {/* Quick Add Buttons */}
            <div className="mt-4 pt-4 border-t border-white/10">
                <div className="text-xs text-white/60 mb-2">Quick Add:</div>
                <div className="flex flex-wrap gap-2">
                    {["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META"].map((symbol) => (
                        <button
                            key={symbol}
                            onClick={() => addSymbol(symbol)}
                            disabled={symbols.includes(symbol)}
                            className="px-2 py-1 text-xs rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {symbol}
                        </button>
                    ))}
                </div>
                
            </div>
        </div>
    );
}