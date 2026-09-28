"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Sparkles, 
  Bell, 
  CheckCircle, 
  ShieldCheck, 
  User as UserIcon,
  LogOut,
  ExternalLink
} from "lucide-react";
import { api, getToken } from "@/lib/api";

export default function Navbar() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (getToken()) {
      api.getNotifications()
        .then((data) => {
          setNotifications(data || []);
          setUnreadCount((data || []).filter((n: any) => !n.is_read).length);
        })
        .catch(() => {});
    }
  }, []);

  const markAllRead = async () => {
    for (const n of notifications) {
      if (!n.is_read) {
        await api.markNotificationRead(n.id).catch(() => {});
      }
    }
    setUnreadCount(0);
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-6 py-3 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
              InternReach AI
            </span>
            <span className="block text-[10px] text-slate-400 font-medium tracking-wide uppercase">
              AI Recruiter & Outreach CRM
            </span>
          </div>
        </Link>

        {/* 2028 Student Focus Pill */}
        <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-700/40 text-indigo-300 text-xs font-medium">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          2028 Grad Engineering Focus
        </div>

        {/* Mock Mode Pill */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-800/80 border border-slate-700 text-slate-400 text-xs">
          <ShieldCheck className="h-3.5 w-3.5 text-cyan-400" />
          Offline Mock Mode Ready
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Responsible AI Badge */}
        <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
          <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
          <span>Human-in-the-Loop Enforced</span>
        </div>

        {/* Notifications Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-colors"
            title="Notifications"
          >
            <Bell className="h-4 w-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 glass-elevated rounded-xl shadow-2xl p-4 z-50">
              <div className="flex items-center justify-between pb-3 border-b border-slate-700 mb-3">
                <span className="font-semibold text-sm text-slate-200">System Notifications</span>
                {unreadCount > 0 && (
                  <button 
                    onClick={markAllRead}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-72 overflow-y-auto space-y-2">
                {notifications.length === 0 ? (
                  <p className="text-xs text-slate-400 py-3 text-center">No notifications</p>
                ) : (
                  notifications.map((n) => (
                    <div 
                      key={n.id} 
                      className={`p-2.5 rounded-lg text-xs border ${
                        n.is_read ? 'bg-slate-900/40 border-slate-800 text-slate-400' : 'bg-indigo-950/30 border-indigo-800/50 text-slate-200'
                      }`}
                    >
                      <div className="font-semibold text-indigo-300">{n.title}</div>
                      <div className="mt-0.5">{n.message}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Pill */}
        <Link 
          href="/profile"
          className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
        >
          <div className="h-6 w-6 rounded-full bg-indigo-600/30 border border-indigo-500/50 flex items-center justify-center text-xs text-indigo-300 font-semibold">
            A
          </div>
          <span className="text-xs font-medium text-slate-300 hidden md:inline">Arjun (2028)</span>
        </Link>
      </div>
    </header>
  );
}
