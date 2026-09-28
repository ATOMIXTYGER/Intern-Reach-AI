"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Sparkles, 
  Search, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  Briefcase, 
  Users, 
  Send, 
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  AlertCircle
} from "lucide-react";
import { api, getToken, setToken } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [actionableOpps, setActionableOpps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [discoverySuccess, setDiscoverySuccess] = useState<string | null>(null);

  useEffect(() => {
    // Automatically login with demo account if no token exists for seamless first-run
    const initData = async () => {
      if (!getToken()) {
        try {
          const authData = await api.login({
            email: "demo.student2028@internreach.ai",
            password: "Password123!"
          });
          setToken(authData.access_token);
        } catch {
          // ignore
        }
      }
      loadDashboard();
    };

    initData();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [statsData, oppsData] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getActionableOpportunities(6).catch(() => [])
      ]);
      setStats(statsData);
      setActionableOpps(oppsData || []);
    } finally {
      setLoading(false);
    }
  };

  const handleRunDiscovery = async () => {
    setDiscovering(true);
    setDiscoverySuccess(null);
    try {
      const discovered = await api.searchOpportunities({
        target_roles: ["Software Engineering Intern", "Backend Engineering Intern", "AI/ML Engineering Intern"],
        graduation_year: 2028,
        locations: ["Bengaluru", "Hyderabad", "Remote"],
      });
      setDiscoverySuccess(`Discovery completed! Verified & updated ${discovered.length} opportunities.`);
      await loadDashboard();
    } catch (err: any) {
      alert(`Discovery error: ${err.message}`);
    } finally {
      setDiscovering(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel p-6 sm:p-8 border border-slate-800">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-transparent rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Target: 2028 Engineering Undergraduate Cohort</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Recruiter Outreach & Internship Intelligence
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
              Discover verified technical internships, research legitimate early-careers recruiters with evidence, and personalize outreach with human approval before sending.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleRunDiscovery}
              disabled={discovering}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium text-sm shadow-lg shadow-indigo-600/20 transition-all cursor-pointer disabled:opacity-50"
            >
              <Search className={`h-4 w-4 ${discovering ? "animate-spin" : ""}`} />
              <span>{discovering ? "Discovering Opportunities..." : "Find Opportunities"}</span>
            </button>
            <Link
              href="/outreach"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-medium transition-all"
            >
              <span>Outreach Queue</span>
              <ArrowRight className="h-4 w-4 text-slate-400" />
            </Link>
          </div>
        </div>

        {discoverySuccess && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{discoverySuccess}</span>
          </div>
        )}
      </div>

      {/* Top Metrics Grid (10 Core Metrics from Section 17) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">New Opportunities</span>
          <div className="text-2xl font-bold text-white">{stats?.new_opportunities ?? 20}</div>
          <span className="text-[11px] text-emerald-400 flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" /> Verified Genuine
          </span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Eligible (2028)</span>
          <div className="text-2xl font-bold text-emerald-400">{stats?.eligible_opportunities ?? 18}</div>
          <span className="text-[11px] text-slate-400">Sophomore friendly</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">High Match (≥75%)</span>
          <div className="text-2xl font-bold text-indigo-400">{stats?.high_match_opportunities ?? 12}</div>
          <span className="text-[11px] text-indigo-300/80">Skill & Project aligned</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Contacts Researched</span>
          <div className="text-2xl font-bold text-cyan-400">{stats?.contacts_researched ?? 15}</div>
          <span className="text-[11px] text-slate-400">Public recruiting proof</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Awaiting Approval</span>
          <div className="text-2xl font-bold text-amber-400">{stats?.awaiting_approval ?? 4}</div>
          <span className="text-[11px] text-amber-300/80">Requires your review</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Messages Sent</span>
          <div className="text-2xl font-bold text-white">{stats?.messages_sent ?? 3}</div>
          <span className="text-[11px] text-slate-400">Manual user delivery</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Total Responses</span>
          <div className="text-2xl font-bold text-slate-200">{stats?.responses ?? 2}</div>
          <span className="text-[11px] text-slate-400">Recruiter replies</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Positive Responses</span>
          <div className="text-2xl font-bold text-emerald-400">{stats?.positive_responses ?? 1}</div>
          <span className="text-[11px] text-emerald-400/80">Active guidance/chats</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Optional Referrals</span>
          <div className="text-2xl font-bold text-purple-400">{stats?.referrals ?? 1}</div>
          <span className="text-[11px] text-slate-400">From peer engineers</span>
        </div>

        <div className="glass-panel p-4 rounded-xl space-y-1">
          <span className="text-xs text-slate-400 font-medium">Interviews Scheduled</span>
          <div className="text-2xl font-bold text-violet-400">{stats?.interviews ?? 1}</div>
          <span className="text-[11px] text-violet-300/80">In pipeline</span>
        </div>
      </div>

      {/* Main Section: Opportunities Needing Attention (Section 17) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Opportunities Needing Attention</h2>
            <p className="text-xs text-slate-400">Prioritized by skills match, graduation eligibility, and contact availability</p>
          </div>
          <Link 
            href="/opportunities" 
            className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <span>View all opportunities</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {actionableOpps.map((opp) => (
            <div key={opp.id} className="glass-card rounded-2xl p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                {/* Header with Company and Match Score */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-xs font-semibold text-indigo-400 tracking-wide uppercase">
                      {opp.company_name}
                    </span>
                    <h3 className="font-semibold text-slate-100 text-sm leading-snug line-clamp-2 mt-0.5">
                      {opp.title}
                    </h3>
                  </div>
                  <div className="shrink-0 flex items-center gap-1 px-2.5 py-1 rounded-full bg-indigo-950/70 border border-indigo-700/50 text-indigo-300 text-xs font-bold">
                    <TrendingUp className="h-3 w-3 text-indigo-400" />
                    <span>{opp.match_score}%</span>
                  </div>
                </div>

                {/* Location and Eligibility Pill */}
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="px-2.5 py-0.5 rounded-md bg-slate-800 text-slate-300">
                    📍 {opp.location}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded-md text-xs font-medium ${
                    opp.eligibility_status === 'eligible' 
                      ? 'badge-eligible' 
                      : 'badge-review'
                  }`}>
                    {opp.eligibility_status === 'eligible' ? '2028 Eligible' : 'Review Required'}
                  </span>
                </div>

                {/* Recruiter Contact info if known */}
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
                  <div className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
                    <Users className="h-3 w-3 text-cyan-400" />
                    <span>Key Recruiter Contact:</span>
                  </div>
                  {opp.has_contact ? (
                    <div>
                      <div className="font-semibold text-slate-200">{opp.contact_name}</div>
                      <div className="text-[11px] text-slate-400 line-clamp-1">{opp.contact_title}</div>
                    </div>
                  ) : (
                    <div className="text-slate-400 italic">No direct contact linked yet</div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <Link
                  href={`/opportunities/${opp.id}`}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
                >
                  View Details
                </Link>

                <div className="flex items-center gap-1.5">
                  <a
                    href={opp.application_url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                    title="Open Official Job Posting"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>

                  {opp.contact_id ? (
                    <Link
                      href={`/outreach?contact_id=${opp.contact_id}&opportunity_id=${opp.id}`}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors shadow-sm"
                    >
                      Outreach
                    </Link>
                  ) : (
                    <Link
                      href={`/opportunities/${opp.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
                    >
                      Research Contact
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
