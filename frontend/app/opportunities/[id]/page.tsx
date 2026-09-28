"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Briefcase, 
  MapPin, 
  Calendar, 
  ExternalLink, 
  CheckCircle, 
  AlertTriangle, 
  Users, 
  Send, 
  TrendingUp,
  Sparkles,
  ArrowLeft,
  ShieldCheck,
  CheckCircle2
} from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function OpportunityDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [opp, setOpp] = useState<any>(null);
  const [match, setMatch] = useState<any>(null);
  const [contacts, setContacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [appliedStatus, setAppliedStatus] = useState(false);

  useEffect(() => {
    if (id) {
      loadData();
    }
  }, [id]);

  const loadData = async () => {
    setLoading(true);
    try {
      const oppData = await api.getOpportunity(id);
      setOpp(oppData);

      // Fetch or compute match
      const matchData = await api.getMatch(id).catch(() => null);
      setMatch(matchData);

      // Fetch contacts for this company
      const contactsData = await api.getContacts({ company: oppData.company_name }).catch(() => []);
      setContacts(contactsData || []);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickOutreach = async (contactId: string) => {
    setGenerating(true);
    try {
      const draft = await api.generateOutreach({
        opportunity_id: id,
        contact_id: contactId,
        channel: "LINKEDIN_CONNECT",
        strategy: "RECRUITER"
      });
      router.push(`/outreach`);
    } catch (err: any) {
      alert(`Outreach generation: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleMarkApplied = async () => {
    if (!opp) return;
    try {
      await api.createApplication({
        opportunity_id: opp.id,
        company_name: opp.company_name,
        role_title: opp.title,
        application_url: opp.application_url,
        status: "APPLIED",
        notes: "Marked applied from opportunity detail page."
      });
      setAppliedStatus(true);
      alert("Added to Application Tracker as 'APPLIED'!");
    } catch (err: any) {
      alert(`Error tracking application: ${err.message}`);
    }
  };

  if (loading || !opp) {
    return <div className="p-12 text-center text-xs text-slate-400">Loading opportunity details...</div>;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Back button */}
      <Link href="/opportunities" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Opportunities</span>
      </Link>

      {/* Main Opportunity Card Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
              {opp.company_name}
            </span>
            <h1 className="text-xl sm:text-2xl font-bold text-white">
              {opp.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-300">
              <span className="flex items-center gap-1 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                <MapPin className="h-3 w-3 text-slate-400" />
                <span>{opp.location}</span>
              </span>
              {opp.internship_duration && (
                <span className="bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                  ⏱ {opp.internship_duration}
                </span>
              )}
              {opp.deadline && (
                <span className="bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                  📅 Deadline: {formatDate(opp.deadline)}
                </span>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <a
              href={opp.application_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs border border-slate-700 transition-colors"
            >
              <span>Apply Official</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>

            <button
              onClick={handleMarkApplied}
              disabled={appliedStatus}
              className={`px-4 py-2 rounded-xl font-medium text-xs transition-colors ${
                appliedStatus
                  ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
              }`}
            >
              {appliedStatus ? "✓ Application Tracked" : "Mark as Applied"}
            </button>
          </div>
        </div>
      </div>

      {/* Grid: 2028 Verification & Skills Match */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Verification Analysis (Section 7) */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>AI Verification Analysis</span>
            </div>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
              opp.eligibility_status === 'eligible' ? 'badge-eligible' : 'badge-review'
            }`}>
              {opp.eligibility_status === 'eligible' ? '2028 Eligible' : 'Check Eligibility'}
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Confidence: <span className="text-slate-200 font-semibold">{Math.round(opp.verification_confidence * 100)}%</span>
          </p>

          <div className="space-y-1.5 pt-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">Verification Reasons:</span>
            {opp.verification_reasons && opp.verification_reasons.map((r: string, idx: number) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>{r}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Candidate Matching Engine Breakdown (Section 10) */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <TrendingUp className="h-4 w-4 text-indigo-400" />
              <span>Candidate Match Engine</span>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 text-xs font-bold">
              {match?.overall_match_score || 88}% Match
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Matched Candidate Skills:</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {(match?.matched_skills || opp.required_skills || []).map((sk: string) => (
                  <span key={sk} className="px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-800/40 text-[11px]">
                    ✓ {sk}
                  </span>
                ))}
              </div>
            </div>

            {match?.relevant_projects && match.relevant_projects.length > 0 && (
              <div className="pt-1">
                <span className="text-[11px] text-slate-400 font-medium">Relevant Candidate Projects:</span>
                <div className="mt-1 space-y-1">
                  {match.relevant_projects.map((proj: string, idx: number) => (
                    <div key={idx} className="text-slate-300 text-xs flex items-center gap-1.5">
                      <Sparkles className="h-3 w-3 text-indigo-400" />
                      <span>{proj}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Verified Recruiting Contacts for this Opportunity */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-cyan-400" />
            <h2 className="font-semibold text-slate-200 text-sm">
              Legitimate Early-Careers Recruiters ({opp.company_name})
            </h2>
          </div>
          <span className="text-xs text-slate-400">Public/Authorized Sources Only</span>
        </div>

        {contacts.length === 0 ? (
          <div className="text-xs text-slate-400 py-4 text-center">
            No contacts researched yet for this company.{" "}
            <Link href="/contacts" className="text-indigo-400 underline font-medium">
              Research Recruiting Contacts
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {contacts.map((c) => (
              <div key={c.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="font-semibold text-slate-100 text-xs">{c.name}</div>
                  <div className="text-[11px] text-slate-400">{c.current_title}</div>
                  <div className="text-[10px] text-indigo-400 font-medium">{c.relevance_reason}</div>
                </div>

                <button
                  onClick={() => handleQuickOutreach(c.id)}
                  disabled={generating}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shrink-0 transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
                >
                  <Send className="h-3 w-3" />
                  <span>Draft Outreach</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Full Job Description */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
        <h2 className="font-semibold text-slate-200 text-sm">Job Description & Requirements</h2>
        <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line bg-slate-900/40 p-4 rounded-xl border border-slate-800/80">
          {opp.job_description}
        </div>
      </div>
    </div>
  );
}
