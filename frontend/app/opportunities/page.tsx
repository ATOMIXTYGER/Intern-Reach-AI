"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Briefcase, 
  Search, 
  Filter, 
  ExternalLink, 
  CheckCircle, 
  AlertCircle,
  MapPin,
  Calendar,
  Sparkles,
  ArrowRight
} from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);

  // Filters
  const [roleFilter, setRoleFilter] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [eligibilityFilter, setEligibilityFilter] = useState("");
  const [sortBy, setSortBy] = useState("newest");

  useEffect(() => {
    loadOpportunities();
  }, [roleFilter, locationFilter, eligibilityFilter, sortBy]);

  const loadOpportunities = async () => {
    setLoading(true);
    try {
      const data = await api.getOpportunities({
        role: roleFilter || undefined,
        location: locationFilter || undefined,
        eligibility: eligibilityFilter || undefined,
        sort_by: sortBy
      });
      setOpportunities(data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleRunDiscovery = async () => {
    setSearching(true);
    try {
      await api.searchOpportunities({
        target_roles: ["Software Engineering Intern", "Backend Engineering Intern", "AI/ML Engineering Intern"],
        graduation_year: 2028,
        locations: ["Bengaluru", "Hyderabad", "Remote"],
      });
      await loadOpportunities();
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Internship Opportunities</h1>
          <p className="text-xs text-slate-400 mt-1">
            Verified software and AI engineering internships evaluated for 2028 graduation eligibility
          </p>
        </div>

        <button
          onClick={handleRunDiscovery}
          disabled={searching}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-md transition-all cursor-pointer disabled:opacity-50"
        >
          <Sparkles className={`h-3.5 w-3.5 ${searching ? "animate-spin" : ""}`} />
          <span>{searching ? "Discovering..." : "Discover New Internships"}</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center gap-3 border border-slate-800">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="h-4 w-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search by role title (e.g. Backend, SDE, AI)..."
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="w-44">
          <input
            type="text"
            placeholder="Filter location..."
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <select
          value={eligibilityFilter}
          onChange={(e) => setEligibilityFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Eligibilities</option>
          <option value="eligible">Confirmed 2028 Eligible</option>
          <option value="possibly_eligible">Possibly Eligible</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="newest">Sort by: Newest</option>
          <option value="deadline">Sort by: Deadline</option>
          <option value="company">Sort by: Company</option>
        </select>
      </div>

      {/* Opportunities List */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading opportunities...</div>
      ) : opportunities.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-xl border border-slate-800 space-y-3">
          <Briefcase className="h-8 w-8 text-slate-400 mx-auto" />
          <p className="text-sm text-slate-300">No opportunities found matching your filters.</p>
          <button
            onClick={() => { setRoleFilter(""); setLocationFilter(""); setEligibilityFilter(""); }}
            className="text-xs text-indigo-400 hover:text-indigo-300 underline font-medium"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {opportunities.map((opp) => (
            <div key={opp.id} className="glass-card rounded-2xl p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                      {opp.company_name}
                    </span>
                    <h2 className="font-semibold text-slate-100 text-sm mt-0.5 leading-snug">
                      {opp.title}
                    </h2>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold shrink-0 ${
                    opp.eligibility_status === 'eligible' ? 'badge-eligible' : 'badge-review'
                  }`}>
                    {opp.eligibility_status === 'eligible' ? '2028 Eligible' : 'Needs Review'}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300">
                  <span className="flex items-center gap-1 bg-slate-800/80 px-2.5 py-0.5 rounded-md">
                    <MapPin className="h-3 w-3 text-slate-400" />
                    <span>{opp.location}</span>
                  </span>
                  {opp.internship_duration && (
                    <span className="bg-slate-800/80 px-2.5 py-0.5 rounded-md text-slate-300">
                      ⏱ {opp.internship_duration}
                    </span>
                  )}
                  {opp.deadline && (
                    <span className="bg-slate-800/80 px-2.5 py-0.5 rounded-md text-slate-300">
                      📅 Deadline: {formatDate(opp.deadline)}
                    </span>
                  )}
                </div>

                {/* Skills Tags */}
                {opp.required_skills && opp.required_skills.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    {opp.required_skills.slice(0, 5).map((sk: string) => (
                      <span key={sk} className="text-[11px] px-2 py-0.5 rounded-md bg-indigo-950/40 text-indigo-300 border border-indigo-900/40">
                        {sk}
                      </span>
                    ))}
                    {opp.required_skills.length > 5 && (
                      <span className="text-[11px] text-slate-400">+{opp.required_skills.length - 5} more</span>
                    )}
                  </div>
                )}

                {/* Short Snippet */}
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {opp.job_description}
                </p>
              </div>

              {/* Bottom Actions */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-3">
                <Link
                  href={`/opportunities/${opp.id}`}
                  className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  <span>View Details & Verification</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>

                <a
                  href={opp.application_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
                >
                  <span>Apply Link</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
