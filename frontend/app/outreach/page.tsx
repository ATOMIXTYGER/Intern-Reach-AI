"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { 
  Send, 
  CheckCircle, 
  Edit3, 
  XCircle, 
  Copy, 
  Check, 
  ExternalLink, 
  AlertTriangle, 
  ShieldCheck, 
  Sparkles,
  Clock,
  Filter,
  Users
} from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

function OutreachContent() {
  const searchParams = useSearchParams();
  const initialContactId = searchParams.get("contact_id");
  const initialOppId = searchParams.get("opportunity_id");

  const [outreachList, setOutreachList] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("DRAFT"); // Default to Approval Queue!

  // Edit State
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");

  // Copy Feedback
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // New Outreach Composer Modal
  const [showComposer, setShowComposer] = useState(false);
  const [selectedContact, setSelectedContact] = useState(initialContactId || "");
  const [selectedOpp, setSelectedOpp] = useState(initialOppId || "");
  const [selectedChannel, setSelectedChannel] = useState("LINKEDIN_CONNECT");
  const [selectedStrategy, setSelectedStrategy] = useState("RECRUITER");
  const [generating, setGenerating] = useState(false);
  const [duplicateWarnings, setDuplicateWarnings] = useState<string[]>([]);

  useEffect(() => {
    loadAll();
    if (initialContactId) {
      setShowComposer(true);
      setSelectedContact(initialContactId);
      if (initialOppId) setSelectedOpp(initialOppId);
    }
  }, [statusFilter]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [outreachData, contactsData, oppsData] = await Promise.all([
        api.getOutreach({ status: statusFilter === "ALL" ? undefined : statusFilter }),
        api.getContacts(),
        api.getOpportunities()
      ]);
      setOutreachList(outreachData || []);
      setContacts(contactsData || []);
      setOpportunities(oppsData || []);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckDuplicates = async (cId: string, oId?: string) => {
    if (!cId) return;
    try {
      const res = await api.checkDuplicateOutreach(cId, oId);
      setDuplicateWarnings(res.warnings || []);
    } catch {
      // ignore
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedContact) {
      alert("Please select a recruiting contact.");
      return;
    }
    setGenerating(true);
    try {
      await api.generateOutreach({
        contact_id: selectedContact,
        opportunity_id: selectedOpp || null,
        channel: selectedChannel,
        strategy: selectedStrategy
      });
      setShowComposer(false);
      setStatusFilter("DRAFT");
      await loadAll();
    } catch (err: any) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async (id: string, customText?: string) => {
    try {
      await api.approveOutreach(id, {
        approved_by: "Arjun Mehta (2028 Student)",
        edited_content: customText || undefined
      });
      setEditingId(null);
      await loadAll();
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    }
  };

  const handleReject = async (id: string) => {
    if (!confirm("Are you sure you want to dismiss this outreach draft?")) return;
    try {
      await api.rejectOutreach(id);
      await loadAll();
    } catch (err: any) {
      alert(`Reject error: ${err.message}`);
    }
  };

  const handleMarkSent = async (id: string) => {
    try {
      await api.markOutreachSent(id);
      await loadAll();
    } catch (err: any) {
      alert(`Error marking sent: ${err.message}`);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Outreach Queue & CRM</h1>
          <p className="text-xs text-slate-400 mt-1">
            Human-in-the-loop review. Messages are never sent automatically. Review, approve, and send manually.
          </p>
        </div>

        <button
          onClick={() => { setShowComposer(true); setDuplicateWarnings([]); }}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium text-xs shadow-md transition-all cursor-pointer"
        >
          <Sparkles className="h-4 w-4" />
          <span>Compose New Outreach</span>
        </button>
      </div>

      {/* Status Filter Tabs (CRM Lifecycle) */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800">
        {[
          { key: "DRAFT", label: "Awaiting Approval" },
          { key: "APPROVED", label: "Approved (Ready to Send)" },
          { key: "SENT", label: "Sent (Tracking)" },
          { key: "REPLIED", label: "Replied" },
          { key: "POSITIVE", label: "Positive Guidance" },
          { key: "FOLLOW_UP_DUE", label: "Follow-Up Due" },
          { key: "ALL", label: "All Items" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setStatusFilter(tab.key)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
              statusFilter === tab.key
                ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/40 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Outreach Items List */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading outreach messages...</div>
      ) : outreachList.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3">
          <Send className="h-8 w-8 text-slate-400 mx-auto" />
          <p className="text-sm text-slate-300">
            {statusFilter === "DRAFT" 
              ? "No draft messages awaiting approval. All caught up!" 
              : "No outreach records found in this view."}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {outreachList.map((item) => {
            const isEditing = editingId === item.id;
            const contact = item.contact || {};
            const opp = item.opportunity || {};

            return (
              <div 
                key={item.id} 
                className={`glass-panel rounded-2xl p-5 border space-y-4 transition-all ${
                  item.status === 'DRAFT' 
                    ? 'border-amber-500/40 bg-slate-900/70 shadow-lg shadow-amber-500/5' 
                    : item.status === 'APPROVED'
                    ? 'border-emerald-500/40 bg-slate-900/60'
                    : 'border-slate-800'
                }`}
              >
                {/* Header: Company, Role, Contact, Status */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide">
                        {contact.company_name || "Target Company"}
                      </span>
                      {opp.title && (
                        <>
                          <span className="text-slate-400">•</span>
                          <span className="text-xs text-slate-300 font-medium">{opp.title}</span>
                        </>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-semibold text-white">
                        To: {contact.name || "Recruiter"}
                      </h2>
                      <span className="text-xs text-slate-400 font-normal">
                        ({contact.current_title || "Early Careers Recruiting"})
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400 flex items-center gap-2">
                      <span>Channel: <strong className="text-slate-300">{item.channel}</strong></span>
                      <span>•</span>
                      <span>Strategy: <strong className="text-slate-300">{item.strategy}</strong></span>
                      <span>•</span>
                      <span>Version: <strong className="text-slate-300">{item.message_version}</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                      item.status === 'DRAFT'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : item.status === 'APPROVED'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : item.status === 'SENT'
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        : 'bg-slate-800 text-slate-300'
                    }`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Evidence & Why Relevant */}
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-semibold">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Evidence & Operational Alignment:</span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    {item.personalization_reason || contact.relevance_reason}
                  </p>
                </div>

                {/* Message Content Box */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-semibold uppercase tracking-wider text-[10px]">
                      Message Draft (Strict Base Prompt Compliant)
                    </span>
                    <button
                      onClick={() => handleCopy(item.id, item.content)}
                      className="inline-flex items-center gap-1 text-slate-400 hover:text-white transition-colors cursor-pointer text-[11px]"
                    >
                      {copiedId === item.id ? (
                        <>
                          <Check className="h-3.5 w-3.5 text-emerald-400" />
                          <span className="text-emerald-400 font-medium">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3.5 w-3.5" />
                          <span>Copy Message</span>
                        </>
                      )}
                    </button>
                  </div>

                  {isEditing ? (
                    <div className="space-y-2">
                      <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        rows={4}
                        className="w-full bg-slate-950 border border-indigo-500/50 rounded-xl p-3 text-xs text-slate-200 focus:outline-none leading-relaxed"
                      />
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleApprove(item.id, editContent)}
                          className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                        >
                          Save & Approve
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-200 leading-relaxed font-sans select-text">
                      {item.content}
                    </div>
                  )}
                </div>

                {/* Human-in-the-Loop Action Bar (Section 14 & 42) */}
                <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    {contact.public_profile_url && (
                      <a
                        href={contact.public_profile_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
                      >
                        <span>Open Recruiter Profile</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {item.status === "DRAFT" && (
                      <>
                        <button
                          onClick={() => { setEditingId(item.id); setEditContent(item.content); }}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors cursor-pointer"
                        >
                          <Edit3 className="h-3 w-3 text-slate-400" />
                          <span>Edit</span>
                        </button>

                        <button
                          onClick={() => handleReject(item.id)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 text-xs font-medium border border-rose-800/40 transition-colors cursor-pointer"
                        >
                          <XCircle className="h-3 w-3 text-rose-400" />
                          <span>Reject</span>
                        </button>

                        <button
                          onClick={() => handleApprove(item.id)}
                          className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm transition-colors cursor-pointer"
                        >
                          <CheckCircle className="h-3.5 w-3.5" />
                          <span>Approve Message</span>
                        </button>
                      </>
                    )}

                    {item.status === "APPROVED" && (
                      <button
                        onClick={() => handleMarkSent(item.id)}
                        className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-sm transition-colors cursor-pointer"
                      >
                        <Send className="h-3.5 w-3.5" />
                        <span>Mark Sent (Track Follow-Up)</span>
                      </button>
                    )}

                    {item.status === "SENT" && (
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5 text-blue-400" />
                        <span>Sent on {formatDate(item.sent_at)} • 7-day follow-up scheduled</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* New Outreach Composer Modal */}
      {showComposer && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-elevated w-full max-w-lg rounded-2xl p-6 border border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <h2 className="font-bold text-base text-white flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-400" />
                <span>Generate Targeted Outreach Message</span>
              </h2>
              <button 
                onClick={() => setShowComposer(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleGenerate} className="space-y-4 text-xs">
              {/* Select Recruiter Contact */}
              <div className="space-y-1">
                <label className="text-slate-300 font-semibold">Select Recruiter / Contact *</label>
                <select
                  value={selectedContact}
                  onChange={(e) => {
                    setSelectedContact(e.target.value);
                    handleCheckDuplicates(e.target.value, selectedOpp);
                  }}
                  required
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">Choose contact...</option>
                  {contacts.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} — {c.current_title} ({c.company_name})
                    </option>
                  ))}
                </select>
              </div>

              {/* Select Opportunity */}
              <div className="space-y-1">
                <label className="text-slate-300 font-semibold">Select Target Opportunity (Optional)</label>
                <select
                  value={selectedOpp}
                  onChange={(e) => {
                    setSelectedOpp(e.target.value);
                    handleCheckDuplicates(selectedContact, e.target.value);
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">General Early Careers Outreach</option>
                  {opportunities.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.company_name} — {o.title}
                    </option>
                  ))}
                </select>
              </div>

              {/* Duplicate Warnings */}
              {duplicateWarnings.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs space-y-1">
                  <div className="font-semibold flex items-center gap-1 text-amber-200">
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                    <span>Duplicate Outreach Warning:</span>
                  </div>
                  {duplicateWarnings.map((w, i) => (
                    <p key={i}>• {w}</p>
                  ))}
                </div>
              )}

              {/* Strategy & Channel */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-300 font-semibold">Channel</label>
                  <select
                    value={selectedChannel}
                    onChange={(e) => setSelectedChannel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
                  >
                    <option value="LINKEDIN_CONNECT">LinkedIn Connection</option>
                    <option value="LINKEDIN_MESSAGE">LinkedIn Outreach</option>
                    <option value="EMAIL">Email</option>
                    <option value="REFERRAL_REQUEST">Referral Request</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-300 font-semibold">Strategy</label>
                  <select
                    value={selectedStrategy}
                    onChange={(e) => setSelectedStrategy(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
                  >
                    <option value="RECRUITER">University Recruiter</option>
                    <option value="HIRING_MANAGER">Hiring Manager</option>
                    <option value="EMPLOYEE">Peer Engineer / Referral</option>
                    <option value="EXISTING_CONNECTION">Existing Connection</option>
                  </select>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-700">
                <button
                  type="button"
                  onClick={() => setShowComposer(false)}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating || !selectedContact}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-colors disabled:opacity-50 cursor-pointer"
                >
                  <Sparkles className={`h-3.5 w-3.5 ${generating ? "animate-spin" : ""}`} />
                  <span>{generating ? "Generating Draft..." : "Generate AI Draft"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function OutreachPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-400">Loading Outreach Queue...</div>}>
      <OutreachContent />
    </Suspense>
  );
}
