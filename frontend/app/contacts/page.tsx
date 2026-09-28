"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Users, 
  Search, 
  ExternalLink, 
  Send, 
  ShieldCheck, 
  Sparkles,
  CheckCircle2,
  Building,
  UserCheck
} from "lucide-react";
import { api } from "@/lib/api";

export default function ContactsPage() {
  const [contacts, setContacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [companySearch, setCompanySearch] = useState("");
  const [researchCompany, setResearchCompany] = useState("");
  const [researching, setResearching] = useState(false);

  useEffect(() => {
    loadContacts();
  }, [companySearch]);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const data = await api.getContacts({ company: companySearch || undefined });
      setContacts(data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleResearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!researchCompany.trim()) return;
    setResearching(true);
    try {
      await api.researchContacts({ company_name: researchCompany.trim() });
      setResearchCompany("");
      await loadContacts();
    } catch (err: any) {
      alert(`Research failed: ${err.message}`);
    } finally {
      setResearching(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Recruiting Contacts</h1>
          <p className="text-xs text-slate-400 mt-1">
            Legitimate university, campus, and technical recruiting contacts from public verified sources
          </p>
        </div>

        {/* Research Input Form */}
        <form onSubmit={handleResearch} className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Research company (e.g. Razorpay)..."
            value={researchCompany}
            onChange={(e) => setResearchCompany(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 w-56"
          />
          <button
            type="submit"
            disabled={researching || !researchCompany.trim()}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-sm transition-all disabled:opacity-50 cursor-pointer"
          >
            <Sparkles className={`h-3.5 w-3.5 ${researching ? "animate-spin" : ""}`} />
            <span>{researching ? "Researching..." : "Research"}</span>
          </button>
        </form>
      </div>

      {/* Filter */}
      <div className="glass-panel p-4 rounded-xl flex items-center gap-3 border border-slate-800">
        <div className="flex-1 relative">
          <Search className="h-4 w-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by company name..."
            value={companySearch}
            onChange={(e) => setCompanySearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Contacts Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading recruiting contacts...</div>
      ) : contacts.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-xl border border-slate-800 space-y-3">
          <Users className="h-8 w-8 text-slate-400 mx-auto" />
          <p className="text-sm text-slate-300">No recruiting contacts found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.map((contact) => (
            <div key={contact.id} className="glass-card rounded-2xl p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wide">
                      {contact.company_name}
                    </span>
                    <h2 className="font-semibold text-slate-100 text-sm mt-0.5">
                      {contact.name}
                    </h2>
                    <p className="text-xs text-slate-300 mt-0.5">{contact.current_title}</p>
                  </div>

                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold shrink-0 ${
                    contact.operational_relevance === 'high' 
                      ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800' 
                      : 'bg-indigo-950/80 text-indigo-300 border border-indigo-800'
                  }`}>
                    {contact.operational_relevance.toUpperCase()} RELEVANCE
                  </span>
                </div>

                {/* Evidence snippet */}
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-medium">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Public Evidence Verified</span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    {contact.relevance_reason}
                  </p>
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                {contact.public_profile_url ? (
                  <a
                    href={contact.public_profile_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    <span>View Public Profile</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                ) : (
                  <span className="text-[11px] text-slate-400">Public directory verified</span>
                )}

                <Link
                  href={`/outreach?contact_id=${contact.id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-sm transition-colors"
                >
                  <Send className="h-3 w-3" />
                  <span>Draft Outreach</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
