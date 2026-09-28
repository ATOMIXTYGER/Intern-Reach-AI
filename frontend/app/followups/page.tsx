"use client";

import React, { useState, useEffect } from "react";
import { 
  Clock, 
  CheckCircle, 
  Send, 
  Edit3, 
  AlertCircle, 
  Copy, 
  Check,
  ShieldAlert
} from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function FollowupsPage() {
  const [followups, setFollowups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    loadFollowups();
  }, []);

  const loadFollowups = async () => {
    setLoading(true);
    try {
      const data = await api.getFollowups();
      setFollowups(data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await api.approveFollowup(id);
      await loadFollowups();
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    }
  };

  const handleMarkSent = async (id: string) => {
    try {
      await api.markFollowupSent(id);
      await loadFollowups();
    } catch (err: any) {
      alert(`Mark sent error: ${err.message}`);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Follow-Up Cadence & Reminders</h1>
        <p className="text-xs text-slate-400 mt-1">
          Responsible follow-up policy: Initial outreach → 7 day pause → 1 polite follow-up → 7-10 day pause → Close.
        </p>
      </div>

      {/* Safety Policy Card */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 flex items-start gap-3">
        <ShieldAlert className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-semibold text-slate-200">Anti-Spam Follow-up Constraint</span>
          <p className="leading-relaxed">
            The agent never sends automated messages or spams recruiters. Follow-ups only generate reminders when due, and require your explicit human approval and manual transmission.
          </p>
        </div>
      </div>

      {/* Follow-up list */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading follow-ups...</div>
      ) : followups.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3">
          <Clock className="h-8 w-8 text-slate-400 mx-auto" />
          <p className="text-sm text-slate-300">No scheduled or pending follow-ups at this time.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {followups.map((item) => (
            <div 
              key={item.id}
              className={`glass-panel rounded-2xl p-5 border space-y-3 ${
                item.status === 'DUE' ? 'border-amber-500/50 bg-slate-900/80 shadow-md' : 'border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                    Follow-up #{item.sequence_number}
                  </span>
                  <span className="text-xs text-slate-400">
                    Due: <strong className="text-slate-200">{formatDate(item.due_date)}</strong> (Cadence: {item.wait_days} days)
                  </span>
                </div>

                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                  item.status === 'DUE' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  item.status === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                  item.status === 'SENT' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                  'bg-slate-800 text-slate-400'
                }`}>
                  {item.status}
                </span>
              </div>

              {/* Message Content */}
              {item.content && (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-semibold text-[10px] uppercase">Message Content</span>
                    <button
                      onClick={() => handleCopy(item.id, item.content)}
                      className="inline-flex items-center gap-1 text-[11px] hover:text-white"
                    >
                      {copiedId === item.id ? (
                        <Check className="h-3 w-3 text-emerald-400" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                      <span>Copy</span>
                    </button>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 leading-relaxed font-sans">
                    {item.content}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-end gap-2">
                {item.status === "DUE" && (
                  <button
                    onClick={() => handleApprove(item.id)}
                    className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors cursor-pointer"
                  >
                    Approve Follow-Up
                  </button>
                )}

                {item.status === "APPROVED" && (
                  <button
                    onClick={() => handleMarkSent(item.id)}
                    className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors cursor-pointer"
                  >
                    Mark Sent
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
