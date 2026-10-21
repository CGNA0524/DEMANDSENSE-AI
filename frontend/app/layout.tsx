import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "DemandSense AI — Demand Forecasting & Inventory Optimization Platform",
  description: "Enterprise SaaS platform for retail demand forecasting, inventory replenishment, and stockout risk management using Machine Learning.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 antialiased font-sans">
        <Navbar />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>DemandSense AI — Intelligent Retail Analytics &amp; Inventory Optimization Platform</span>
            <span>FastAPI Python Engine &bull; Scikit-learn &bull; XGBoost &bull; Next.js</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
