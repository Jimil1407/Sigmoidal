"use client";
import PlaceTrade from "@/components/PlaceTrade";
import LiveData from "@/components/LiveData";
import PortfolioInfo from "@/components/PortfolioInfo";
import { useRef } from "react";

export default function Dashboard() {
  const refreshRef = useRef<null | (() => Promise<void>)>(null);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <nav className="w-full sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-white/5 bg-white/0 border-b border-white/10">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <div className="h-6 w-px bg-white/10" />
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center justify-center w-9 h-9 rounded-full bg-white/10 text-white font-bold text-lg">S</span>
              <span className="font-bold text-xl tracking-tight">sigmoidal</span>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-6 text-sm text-white/80">
            <a className="hover:text-white" href="#portfolio">Portfolio</a>
            <a className="hover:text-white" href="#positions">Positions</a>
            <a className="hover:text-white" href="#trades">Trades</a>
            <a className="hover:text-white" href="#live">Live</a>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => history.back()} className="px-3 py-1.5 rounded-full border border-white/15 hover:bg-white/10 text-xs">Log Out</button>
          </div>
        </div>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-6">
          <PortfolioInfo exposeRefresh={(fn) => { refreshRef.current = fn; }} />
        </div>

        <div className="space-y-6 lg:sticky lg:top-24">
          <PlaceTrade onPlaced={() => refreshRef.current?.()} />
          <LiveData />
        </div>
      </div>
    </div>
  );
}