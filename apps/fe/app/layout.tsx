import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://sigmoidal.app"),
  title: {
    default: "Sigmoidal",
    template: "%s – Sigmoidal",
  },
  description: "AI-powered trading analytics, signals, and portfolio intelligence.",
  applicationName: "Sigmoidal",
  openGraph: {
    title: "Sigmoidal",
    description: "AI-powered trading analytics, signals, and portfolio intelligence.",
    url: "/",
    siteName: "Sigmoidal",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Sigmoidal",
    description: "AI-powered trading analytics, signals, and portfolio intelligence.",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className={`${geistSans.variable} ${geistMono.variable} h-full min-h-screen bg-gradient-to-br from-[#15121C] to-[#0B0C14] text-white antialiased selection:bg-[#7B6CF6]/30 selection:text-white`}>
        {children}
        <ToastContainer position="top-right" theme="dark" closeOnClick newestOnTop pauseOnFocusLoss={false} />
      </body>
    </html>
  );
}
