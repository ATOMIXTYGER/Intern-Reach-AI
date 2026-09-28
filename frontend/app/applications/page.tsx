"use client";

import React, { useState, useEffect } from "react";
import { 
  Kanban, 
  Plus, 
  ExternalLink, 
  Calendar, 
  Clock, 
  Building, 
  CheckCircle,
  FileText
} from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

const STAGES = [
  "SAVED",
  "APPLIED",
  "OA",
  "INTERVIEW",
  "FINAL_ROUND",
  "OFFER",
  "REJECTED",
  "WITHDRAWN"
];

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [companyName, setCompanyName] = useState("");
  const [roleTitle, setRoleTitle] = useState("");
  const [appUrl, setAppUrl] = useState("");
  const [status, setStatus] = useState("APPLIED");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    setLoading(true);
    try {
      const data = await api.getApplications();
      setApplications(data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim() || !roleTitle.trim()) return;

    try {
      await api.createApplication({
        company_name: companyName.trim(),
        role_title: roleTitle.trim(),
        application_url: appUrl.trim() || null,
        status,
        notes: notes.trim() || null,
        next_action: "Monitor status"
      });
      setShowAddModal(false);
      setCompanyName("");
      setRoleTitle("");
      setAppUrl("");
      setNotes("");
      await loadApplications();
    } catch (err: any) {
      alert(`Error creating application: ${err.message}`);
    }
  };

  const handleUpdateStatus = async (appId: string, newStatus: string) => {
    try {
      await api.updateApplication(appId, { status: newStatus });
      await loadApplications();
    } catch (err: any) {
      alert(`Error updating stage: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Application Tracker</h1>
          <p className="text-xs text-slate-400 mt-1">
            Track and manage your recruitment pipeline stages, interview assessments, and offers
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-md transition-all cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          <span>Add Application</span>
        </button>
      </div>

      {/* Applications Table / Cards */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading applications...</div>
      ) : applications.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3">
          <Kanban className="h-8 w-8 text-slate-400 mx-auto" />
          <p className="text-sm text-slate-300">No applications tracked yet.</p>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Company</th>
                  <th className="py-3.5 px-4">Role</th>
                  <th className="py-3.5 px-4">Stage</th>
                  <th className="py-3.5 px-4">Applied Date</th>
                  <th className="py-3.5 px-4">Next Action / Notes</th>
                  <th className="py-3.5 px-4 text-right">Links</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-100">
                      {app.company_name}
                    </td>
                    <td className="py-3.5 px-4 text-slate-200">
                      {app.role_title}
                    </td>
                    <td className="py-3.5 px-4">
                      <select
                        value={app.status}
                        onChange={(e) => handleUpdateStatus(app.id, e.target.value)}
                        className={`text-[11px] font-semibold px-2.5 py-1 rounded-lg border focus:outline-none ${
                          app.status === 'OFFER' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' :
                          app.status === 'INTERVIEW' || app.status === 'FINAL_ROUND' ? 'bg-violet-950/80 text-violet-300 border-violet-800' :
                          app.status === 'OA' ? 'bg-amber-950/80 text-amber-300 border-amber-800' :
                          app.status === 'REJECTED' ? 'bg-rose-950/40 text-rose-400 border-rose-800/40' :
                          'bg-slate-900 text-slate-300 border-slate-800'
                        }`}
                      >
                        {STAGES.map((st) => (
                          <option key={st} value={st}>{st.replace('_', ' ')}</option>
                        ))}
                      </select>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {formatDate(app.date_applied)}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 max-w-xs truncate">
                      {app.next_action || app.notes || "—"}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {app.application_url && (
                        <a
                          href={app.application_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-slate-400 hover:text-white"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-elevated w-full max-w-md rounded-2xl p-6 border border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <h2 className="font-bold text-sm text-white">Track Application</h2>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreate} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="text-slate-300 font-semibold">Company Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Razorpay"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-semibold">Role Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Software Engineering Intern"
                  value={roleTitle}
                  onChange={(e) => setRoleTitle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-300 font-semibold">Initial Stage</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
                  >
                    {STAGES.map((st) => (
                      <option key={st} value={st}>{st.replace('_', ' ')}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-300 font-semibold">Application URL</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={appUrl}
                    onChange={(e) => setAppUrl(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-semibold">Notes / Next Action</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Referral from senior engineer; OA received."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-700">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md"
                >
                  Track Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
