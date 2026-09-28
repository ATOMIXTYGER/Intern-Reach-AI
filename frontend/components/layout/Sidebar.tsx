"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  Send, 
  Kanban, 
  Clock, 
  BarChart3, 
  UserCircle, 
  Settings,
  Sparkles,
  ShieldCheck
} from "lucide-react";
import { api, getToken } from "@/lib/api";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Opportunities", href: "/opportunities", icon: Briefcase },
  { name: "Contacts", href: "/contacts", icon: Users },
  { name: "Outreach CRM", href: "/outreach", icon: Send, badgeKey: "awaiting_approval" },
  { name: "Applications", href: "/applications", icon: Kanban },
  { name: "Follow-ups", href: "/followups", icon: Clock },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Profile & Resume", href: "/profile", icon: UserCircle },
  { name: "Settings & Admin", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    if (getToken()) {
      api.getDashboardStats().then(setStats).catch(() => {});
    }
  }, [pathname]);

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 flex flex-col h-[calc(100vh-61px)] sticky top-[61px] select-none p-4 justify-between">
      <div className="space-y-6">
        {/* Navigation list */}
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            const badgeCount = item.badgeKey && stats ? stats[item.badgeKey] : 0;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4 w-4 ${isActive ? "text-indigo-400" : "text-slate-400"}`} />
                  <span>{item.name}</span>
                </div>
                {badgeCount > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    {badgeCount}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Safety Policy Reminder Box */}
      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1.5 text-slate-400">
        <div className="flex items-center gap-1.5 font-semibold text-slate-300">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Outreach Safety</span>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-400">
          No automated spam or scraping. Every message requires your explicit human review before sending.
        </p>
      </div>
    </aside>
  );
}
