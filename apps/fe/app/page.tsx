import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#15121C] to-[#0B0C14] text-white flex flex-col">
      <nav className="w-full sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-white/5 bg-white/0 border-b border-white/10">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center w-9 h-9 rounded-full bg-white/10 text-white font-bold text-lg">S</span>
            <span className="font-bold text-xl tracking-tight">sigmoidal</span>
          </div>
          <div className="hidden sm:flex items-center gap-6 text-sm text-white/80">
            <a className="hover:text-white" href="#features">Features</a>
            <a className="hover:text-white" href="#how">How it works</a>
            <a className="hover:text-white" href="#pricing">Pricing</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/signin" className="px-4 py-2 rounded-full border border-white/15 hover:bg-white/10">Sign in</Link>
            <Link href="/signup" className="px-4 py-2 rounded-full bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Get Started</Link>
          </div>
        </div>
      </nav>

      <main className="flex-1">
        {/* Hero */}
        <section className="relative">
          <div className="absolute inset-0 pointer-events-none [mask-image:radial-gradient(ellipse_at_center,black,transparent_65%)]">
            <div className="absolute -top-16 left-1/2 -translate-x-1/2 w-[1200px] h-[1200px] rounded-full bg-[#7B6CF6]/10 blur-3xl" />
          </div>
          <div className="max-w-6xl mx-auto px-4 pt-20 pb-14">
            <div className="inline-flex items-center gap-2 text-xs text-white/70 bg-white/5 border border-white/10 px-3 py-1 rounded-full">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              Live signals and portfolio insights
            </div>
            <h1 className="mt-6 text-center sm:text-left text-4xl sm:text-6xl font-extrabold leading-tight">
              Trade smarter with
              <span className="mx-2 text-transparent bg-clip-text bg-gradient-to-r from-white via-[#b7afff] to-[#7B6CF6]">Sigmoidal</span>
              intelligence
            </h1>
            <p className="mt-4 max-w-2xl text-white/80 text-base sm:text-lg">
              A modern analytics dashboard for markets: real‑time streams, ML predictions,
              and a distraction‑free workflow. Built for speed and clarity.
            </p>
            <div className="mt-8 flex items-center gap-3">
              <Link href="/signup" className="px-6 py-3 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold shadow-lg shadow-[#7B6CF6]/20">
                Create free account
              </Link>
              <Link href="/signin" className="px-6 py-3 rounded-xl border border-white/15 hover:bg-white/10">
                Sign in
              </Link>
            </div>

            <div className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-2xl font-bold">99.9%</div>
                <div className="text-xs text-white/60">Uptime for market streams</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-2xl font-bold"><span className="text-[#b7afff]">2.3ms</span></div>
                <div className="text-xs text-white/60">Median response latency</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-2xl font-bold">+18%</div>
                <div className="text-xs text-white/60">Avg. strategy lift from ML</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="text-2xl font-bold">24/7</div>
                <div className="text-xs text-white/60">Global support</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="border-t border-white/10 bg-white/0">
          <div className="max-w-6xl mx-auto px-4 py-14">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="text-xs font-mono text-white/60">feature.real_time_data</div>
                <h3 className="mt-2 text-xl font-semibold">Real-time market streams</h3>
                <p className="mt-2 text-white/70 text-sm">
                  Stream tick data and portfolio events with sub‑second latency. No noise, just what matters.
                </p>
                <ul className="mt-3 text-xs text-white/60 list-disc list-inside space-y-1">
                  <li>WebSocket push updates</li>
                  <li>Backfill and replay</li>
                  <li>Smart throttling</li>
                </ul>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="text-xs font-mono text-white/60">feature.ai_signals</div>
                <h3 className="mt-2 text-xl font-semibold">ML predictions & signals</h3>
                <p className="mt-2 text-white/70 text-sm">
                  Integrate model outputs for entries, exits, and risk. Transparent confidence and drift checks.
                </p>
                <ul className="mt-3 text-xs text-white/60 list-disc list-inside space-y-1">
                  <li>Per‑asset confidence bands</li>
                  <li>Explainability summaries</li>
                  <li>Auto retraining hooks</li>
                </ul>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="text-xs font-mono text-white/60">feature.security</div>
                <h3 className="mt-2 text-xl font-semibold">Security by default</h3>
                <p className="mt-2 text-white/70 text-sm">
                  Private by design: minimal surface area, encrypted transport, and per‑scope API keys.
                </p>
                <ul className="mt-3 text-xs text-white/60 list-disc list-inside space-y-1">
                  <li>Row‑level access</li>
                  <li>Audit trails</li>
                  <li>Granular roles</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="border-t border-white/10">
          <div className="max-w-6xl mx-auto px-4 py-14">
            <div className="mb-8">
              <div className="text-xs uppercase tracking-widest text-white/60">Workflow</div>
              <h2 className="text-2xl sm:text-3xl font-bold">From data to decision in 3 steps</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <div className="text-sm text-white/60">01</div>
                <h4 className="mt-1 font-semibold">Connect sources</h4>
                <p className="mt-2 text-sm text-white/70">Link your brokers, datasets, and strategies. Import positions in minutes.</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <div className="text-sm text-white/60">02</div>
                <h4 className="mt-1 font-semibold">Stream & analyze</h4>
                <p className="mt-2 text-sm text-white/70">Watch real‑time signals and P&L with keyboard‑first navigation.</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                <div className="text-sm text-white/60">03</div>
                <h4 className="mt-1 font-semibold">Automate actions</h4>
                <p className="mt-2 text-sm text-white/70">Trigger alerts or orders when thresholds hit. Keep full control.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing teaser */}
        <section id="pricing" className="border-t border-white/10">
          <div className="max-w-6xl mx-auto px-4 py-14">
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 sm:p-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h3 className="text-xl font-semibold">Simple, transparent pricing</h3>
                  <p className="text-white/70 text-sm mt-1">Start free. Upgrade when you need more streams and seats.</p>
                </div>
                <div className="flex items-center gap-3">
                  <Link href="/signup" className="px-5 py-2.5 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Try Free</Link>
                  <Link href="/signin" className="px-5 py-2.5 rounded-xl border border-white/15 hover:bg-white/10">Sign In</Link>
                </div>
              </div>
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="font-semibold">Free</div>
                  <div className="text-white/60">Core features, 1 seat</div>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="font-semibold">Pro</div>
                  <div className="text-white/60">Advanced signals, 5 seats</div>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="font-semibold">Enterprise</div>
                  <div className="text-white/60">Custom SLAs & security</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t border-white/10">
          <div className="max-w-6xl mx-auto px-4 py-14">
            <div className="relative rounded-2xl p-[1px] bg-gradient-to-r from-white/10 via-[#7B6CF6]/30 to-white/10">
              <div className="rounded-2xl bg-[#0B0C14] p-8">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <h3 className="text-xl font-semibold">Ready to build your edge?</h3>
                    <p className="text-white/70 text-sm mt-1">Spin up your dashboard in under 2 minutes.</p>
                  </div>
                  <Link href="/signup" className="px-6 py-3 rounded-xl bg-[#7B6CF6] hover:bg-[#9486ff] font-semibold">Get started</Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="w-full border-t border-white/10">
        <div className="max-w-6xl mx-auto p-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/70">
          <div>© 2025 sigmoidal</div>
          <div className="flex items-center gap-4">
            <a className="hover:text-white" href="#">Status</a>
            <a className="hover:text-white" href="#">Privacy</a>
            <a className="hover:text-white" href="#">Terms</a>
            <a className="hover:text-white" href="mailto:support@sigmoidal.com">Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
