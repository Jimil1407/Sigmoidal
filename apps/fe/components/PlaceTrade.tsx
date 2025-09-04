import axios from "axios";
import { toast } from "react-toastify";
export default function PlaceTrade() {
    const handleSubmitTrade = async (e: React.FormEvent) => {
    try {
    e.preventDefault();
    const token = typeof window !== "undefined" ? window.localStorage.getItem("token") : null;
    if (!token) return;
    const authHeader = { Authorization: token } as const;
    const quantity = (e.target as HTMLFormElement).quantity.value;
    const stockSymbol = (e.target as HTMLFormElement).stockSymbol.value;
    const tradeType = (e.target as HTMLFormElement).tradeType.value;
    const price = await axios.get(`http://localhost:8080/api/v1/market/quote/${stockSymbol}`, { headers: authHeader });
    await axios.post(`http://localhost:8080/api/v1/portfolio/myportfolio/trade`, { quantity, stockSymbol, tradeType, price: price.data.price }, { headers: authHeader });
        toast.success("Trade placed successfully");
    } catch (error) {
        toast.error("Error placing trade");
        console.error(error);
    }
};
return (
    <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-5">
        <h2 className="text-lg font-semibold mb-4">Place Order</h2>
        <form onSubmit={handleSubmitTrade} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
                <input className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" type="text" name="quantity" placeholder="Quantity" />
                <input className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]" type="text" name="stockSymbol" placeholder="Stock Symbol" />
            </div>
            <select name="tradeType" className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]">
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
            </select>
            <button type="submit" className="w-full px-4 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Place Trade</button>
        </form>
    </div>
);
}

