"use client";

type MarketData = {
    symbol: string;
    current: number;
    high: number;
    low: number;
    change: number;
    percent_change: number;
    lastUpdated?: number;
};

type MarketCardProps = {
    symbol: string;
    onRemove: () => void;
    data?: MarketData | null;
    isRealTime?: boolean;
};

export default function MarketCard({ symbol, onRemove, data, isRealTime = false }: MarketCardProps) {

    const isPositive = data?.change && data.change >= 0;
    const isNegative = data?.change && data.change < 0;

    return (
        <div className="relative rounded-xl border border-white/10 bg-gradient-to-br from-[#0B0C14]/95 to-[#0B0C14]/90 p-4 backdrop-blur-sm">
            {/* Remove Button */}
            <div className="absolute top-3 right-3">
                <button
                    onClick={onRemove}
                    className="text-white/40 hover:text-white/70 text-xs px-2 py-1 rounded hover:bg-white/5 transition-colors"
                >
                    Unsubscribe
                </button>
            </div>

            {/* Symbol */}
            <div className="mb-3">
                <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-white">{symbol}</h3>
                    {isRealTime && (
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-xs text-green-400 font-medium">Live</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Current Price */}
            <div className="mb-4">
                <div className="text-2xl font-bold text-white">
                    ${data?.current?.toFixed(2) || "—"}
                </div>
                <div className={`text-sm font-medium flex items-center gap-1 ${
                    isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-white/60'
                }`}>
                    {data?.change !== undefined && data?.change !== 0 && (
                        <>
                            <span>{isPositive ? '↗' : '↘'}</span>
                            <span>${Math.abs(data.change).toFixed(2)}</span>
                            <span>({data.percent_change?.toFixed(2)}%)</span>
                        </>
                    )}
                    {(!data?.change || data.change === 0) && (
                        <span className="text-white/60">No change</span>
                    )}
                </div>
            </div>

            {/* High/Low */}
            <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 rounded-lg p-3">
                    <div className="text-xs text-white/60 mb-1">Today's High</div>
                    <div className="text-sm font-semibold text-green-400">
                        ${data?.high?.toFixed(2) || "—"}
                    </div>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                    <div className="text-xs text-white/60 mb-1">Today's Low</div>
                    <div className="text-sm font-semibold text-red-400">
                        ${data?.low?.toFixed(2) || "—"}
                    </div>
                </div>
            </div>

            {/* Loading State */}
            {!data && (
                <div className="absolute inset-0 bg-[#0B0C14]/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <div className="text-white/60 text-sm">Loading...</div>
                </div>
            )}
        </div>
    );
}
