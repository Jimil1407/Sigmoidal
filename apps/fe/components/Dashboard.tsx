"use client";
import PlaceTrade from "@/components/PlaceTrade";
import LiveData from "@/components/LiveData";
import PortfolioInfo from "@/components/PortfolioInfo";
import { useRef, useState } from "react";
import PredictPage from "@/app/predict/page";

export default function Dashboard() {
  const refreshRef = useRef<null | (() => Promise<void>)>(null);
  const [activeSection, setActiveSection] = useState("portfolio");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: "portfolio", label: "Portfolio", href: "#portfolio" },
    { id: "positions", label: "Positions", href: "#positions" },
    { id: "trades", label: "Trades", href: "#trades" },
    { id: "predict", label: "Predict", href: "#predict" }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <nav className="w-full sticky top-0 z-10 backdrop-blur-md bg-[#0B0C14]/80 border-b border-white/10 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          {/* Logo Section */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] rounded-full blur-sm opacity-75 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative inline-flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] text-white font-bold text-lg shadow-lg">
                  S
                </span>
              </div>
              <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
                sigmoidal
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1 bg-white/5 rounded-full p-1 backdrop-blur-sm">
            {navItems.map((item) => (
              <a
                key={item.id}
                href={item.href}
                onClick={() => setActiveSection(item.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  activeSection === item.id
                    ? "bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] text-white shadow-lg"
                    : "text-white/70 hover:text-white hover:bg-white/10"
                }`}
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* User Actions */}
          <div className="flex items-center gap-3">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/80 hover:text-white transition-all duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <button 
              onClick={() => {
                localStorage.removeItem("token");
                window.location.href = "/signin";
              }} 
              className="group relative px-4 py-2 rounded-full border border-white/20 hover:border-white/30 bg-white/5 hover:bg-white/10 text-sm font-medium text-white/80 hover:text-white transition-all duration-200 backdrop-blur-sm"
            >
              <span className="relative z-10 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="hidden sm:inline">Log Out</span>
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-white/10 bg-[#0B0C14]/95 backdrop-blur-md">
            <div className="px-4 py-3 space-y-2">
              {navItems.map((item) => (
                <a
                  key={item.id}
                  href={item.href}
                  onClick={() => {
                    setActiveSection(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`block px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    activeSection === item.id
                      ? "bg-gradient-to-r from-[#7B6CF6] to-[#9486ff] text-white"
                      : "text-white/70 hover:text-white hover:bg-white/10"
                  }`}
                >
                  {item.label}
                </a>
              ))}
            </div>
          </div>
        )}
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-6">
          <PortfolioInfo exposeRefresh={(fn) => { refreshRef.current = fn; }} />
        </div>

        <div className="space-y-6 lg:sticky lg:top-24">
          <PlaceTrade onPlaced={() => refreshRef.current?.()} />
          <LiveData />
          <PredictPage />
        </div>
      </div>
    </div>
  );
}