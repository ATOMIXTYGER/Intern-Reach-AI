"use client";

import React, { useState, useEffect } from "react";
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Send, 
  CheckCircle, 
  AlertCircle,
  Building,
  Briefcase
} from "lucide-react";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAnalytics()
      .then(setAnalytics)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading || !analytics) {
    return <div className="p-12 text-center text-xs text-slate-400">Loading analytics...</div>;
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Outreach & Pipeline Analytics</h1>
        <p className="text-xs text-slate-400 mt-1">
          Operational telemetry and conversion rates across discovered opportunities, recruiters, and responses
        </p>
      </div>

      {/* Advisory Banner (Section 37 requirement) */}
      <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-800/60 text-xs text-indigo-300 flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-white">Statistical Advisory Note</span>
          <p className="mt-0.5 leading-relaxed text-slate-300">
            These analytics serve strictly as internal operational metrics for tracking response frequency and application progression. They do not constitute guaranteed hiring probabilities or predictive outcomes.
          </p>
        </div>
      </div>

      {/* Top Conversion Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Recruiter Response Rate</span>
          <div className="text-3xl font-bold text-white">{analytics.response_rate_percent}%</div>
          <span className="text-[11px] text-emerald-400 font-medium">From personalized drafts</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Positive Guidance Rate</span>
          <div className="text-3xl font-bold text-emerald-400">{analytics.positive_response_rate_percent}%</div>
          <span className="text-[11px] text-slate-400">Of received replies</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Referrals Established</span>
          <div className="text-3xl font-bold text-indigo-400">{analytics.referrals_count}</div>
          <span className="text-[11px] text-slate-400">Via peer engineers</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Interviews Secured</span>
          <div className="text-3xl font-bold text-violet-400">{analytics.interviews_count}</div>
          <span className="text-[11px] text-violet-300/80">Active in pipeline</span>
        </div>
      </div>

      {/* Distributions Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Top Target Companies */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Building className="h-4 w-4 text-cyan-400" />
            <span>Opportunities by Target Company</span>
          </div>
          <div className="space-y-2">
            {analytics.top_target_companies.map((tc: any, i: number) => (
              <div key={i} className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="font-medium text-slate-200">{tc.company}</span>
                <div className="flex items-center gap-3 text-slate-400">
                  <span>{tc.opportunities} listings</span>
                  <span className="text-indigo-400 font-semibold">{tc.outreach} outreach</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Opportunity Source Distribution */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Briefcase className="h-4 w-4 text-indigo-400" />
            <span>Opportunity Sources Distribution</span>
          </div>
          <div className="space-y-2">
            {Object.entries(analytics.sources_distribution || {}).map(([src, count]: [string, any], i: number) => (
              <div key={i} className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="font-medium text-slate-200 capitalize">{src.replace(/_/g, " ")}</span>
                <span className="text-indigo-400 font-bold">{count} listings</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
