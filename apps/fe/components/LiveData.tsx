"use client";
import { useEffect, useState } from "react";

export default function LiveData() {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [livePrice, setLivePrice] = useState<number | null>(null);
    const [liveSymbol, setLiveSymbol] = useState<string>("");

    useEffect(() => {
        const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
        if (!token) return;
        const protocol = typeof window !== "undefined" && window.location.protocol === "https:" ? "wss" : "ws";
        const host = process.env.NEXT_PUBLIC_API_HOST ?? "localhost:8080";
        const ws = new WebSocket(`${protocol}://${host}/ws/getlivedata?token=${encodeURIComponent(token)}`);
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
        ws.onerror = () => {
            setSocket(null);
        };
        ws.onclose = () => {
            setSocket(null);
        };
        return () => {
            ws.close();
        };
    }, []);

    return (
        <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
            <h2 className="text-lg font-semibold mb-4">Live Market</h2>
            <form onSubmit={(e) => {
                e.preventDefault();
                const form = e.target as HTMLFormElement;
                const symbol = (form.symbol as HTMLInputElement).value;
                if (!symbol || !socket) return;
                setLiveSymbol(symbol.toUpperCase());
                socket.send(JSON.stringify({ type: "subscribe", symbol }));
                form.reset();
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
    );
}