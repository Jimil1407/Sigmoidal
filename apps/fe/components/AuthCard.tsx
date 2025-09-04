"use client";
import Link from "next/link";
import { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useRouter } from "next/navigation";

type AuthCardProps = {
  mode: "signin" | "signup";
};

export default function AuthCard({ mode }: AuthCardProps) {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isSignup = mode === "signup";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await new Promise((r) => setTimeout(r, 800));
  
      if (isSignup) {
        try {
          await axios.post("http://0.0.0.0:8080/api/v1/users/createUser", { email, password, username });
          toast.success("Account created successfully");
          router.push("/signin");
        } catch (error: any) {
          const message = error?.response?.data?.detail || error?.message || "Error creating account";
          toast.error(message);
          return;
        }
      } else {
        try {
          const response = await axios.post("http://0.0.0.0:8080/api/v1/users/login", { email, password });
          const { token } = response.data;
          toast.success("Logged in successfully");
          localStorage.setItem("token", token);
          router.push("/dashboard");
        } catch (error: any) {
          const message = error?.response?.data?.detail || error?.message || "Error logging in";
          toast.error(message);
          return;
        }
      }
    } finally {
      setIsSubmitting(false);
    }
  }
  
  return (
    <div className="w-full max-w-md mx-auto">
      <div className="relative rounded-2xl p-[1px] bg-gradient-to-br from-white/10 via-[#7B6CF6]/20 to-white/10">
        <div className="rounded-2xl border border-white/10 bg-[#0B0C14]/90 p-6 shadow-xl">
          <div className="mb-5">
            <div className="inline-flex items-center gap-2 text-xs text-white/70 bg-white/5 border border-white/10 px-3 py-1 rounded-full">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              Secure {isSignup ? "account" : "session"}
            </div>
            <h1 className="mt-3 text-2xl font-semibold">
              {isSignup ? "Create your account" : "Welcome back"}
            </h1>
            <p className="text-sm text-white/70 mt-1">
              {isSignup ? "Start your 14‑day free trial." : "Sign in to continue."}
            </p>
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            {isSignup && (
              <label className="block">
                <span className="text-sm text-white/80">Username</span>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="mt-1 w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]"
                  placeholder="yourname"
                />
                <span className="mt-1 block text-xs text-white/50">Used for your profile and sharing.</span>
              </label>
            )}

            <label className="block">
              <span className="text-sm text-white/80">Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 text-sm outline-none focus:border-[#7B6CF6]"
                placeholder="you@sigmoidal.com"
              />
            </label>

            <label className="block">
              <span className="text-sm text-white/80">Password</span>
              <div className="mt-1 relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl bg-[#0B0C14] border border-white/15 px-3 py-2 pr-10 text-sm outline-none focus:border-[#7B6CF6]"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute inset-y-0 right-0 px-3 text-xs text-white/70 hover:text-white"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </label>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-4 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] disabled:opacity-60 disabled:cursor-not-allowed font-semibold"
              aria-busy={isSubmitting}
            >
              {isSubmitting ? (isSignup ? "Creating..." : "Signing in...") : isSignup ? "Create account" : "Sign in"}
            </button>
          </form>

          <div className="mt-5 flex items-center gap-3 text-xs text-white/50">
            <div className="h-px flex-1 bg-white/10" />
            <span>or</span>
            <div className="h-px flex-1 bg-white/10" />
          </div>

          <div className="mt-4 text-center text-sm text-white/70">
            {isSignup ? (
              <span>
                Already have an account?{" "}
                <Link className="text-white hover:underline" href="/signin">Sign in</Link>
              </span>
            ) : (
              <span>
                New to Sigmoidal?{" "}
                <Link className="text-white hover:underline" href="/signup">Create an account</Link>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


