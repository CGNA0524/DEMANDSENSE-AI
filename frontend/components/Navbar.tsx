"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  TrendingUp, 
  Boxes, 
  AlertTriangle, 
  SlidersHorizontal, 
  HelpCircle, 
  Database, 
  FileText,
  Activity,
  Layers
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Overview", icon: BarChart3 },
    { href: "/forecasting", label: "Demand Forecasting", icon: TrendingUp },
    { href: "/inventory", label: "Inventory Planner", icon: Boxes },
    { href: "/stockout-risk", label: "Stockout Risk", icon: AlertTriangle },
    { href: "/optimization", label: "Budget Optimizer", icon: Layers },
    { href: "/simulator", label: "What-If Simulator", icon: SlidersHorizontal },
    { href: "/data-management", label: "Data Hub", icon: Database },
    { href: "/settings", label: "Reports & Settings", icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20 group-hover:bg-blue-700 transition">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <span className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
                  DemandSense <span className="text-xs uppercase bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-semibold border border-blue-200">AI</span>
                </span>
                <p className="text-[11px] text-slate-500 font-medium">Enterprise Forecasting & Optimization</p>
              </div>
            </Link>
          </div>

          {/* Quick status pill */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-full text-xs font-medium text-emerald-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              FastAPI Engine Connected
            </div>
            <Link
              href="/data-management"
              className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition border border-slate-200 flex items-center gap-1.5"
            >
              <Database className="w-3.5 h-3.5 text-slate-500" />
              Manage Data
            </Link>
          </div>
        </div>
      </div>

      {/* Subnav links */}
      <div className="border-t border-slate-100 bg-slate-50/80 backdrop-blur-xs px-4 sm:px-6 lg:px-8 overflow-x-auto scrollbar-none">
        <div className="max-w-7xl mx-auto flex space-x-1 sm:space-x-3 py-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? "bg-white text-blue-700 shadow-2xs font-semibold border border-slate-200/80"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/60"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </header>
  );
}
