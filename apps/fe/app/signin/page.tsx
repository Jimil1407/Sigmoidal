import AuthCard from "@/components/AuthCard";
import Link from "next/link";

export default function SignInPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-12">
      <div className="max-w-6xl mx-auto flex items-center justify-end mb-6">
        <Link href="/" className="inline-flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border border-white/15 bg-white/5 hover:bg-white/10 backdrop-blur-sm transition">
          <span>Why Sigmoidal</span>
          <span aria-hidden>→</span>
        </Link>
      </div>
      <div className="flex items-center justify-center">
        <AuthCard mode="signin" />
      </div>
    </div>
  );
}


