"use client";

import React, { useState, useEffect } from "react";
import { 
  User, 
  Upload, 
  FileText, 
  Save, 
  CheckCircle, 
  Sparkles,
  ShieldCheck,
  Plus,
  Trash2,
  Briefcase
} from "lucide-react";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await api.getProfile();
      setProfile(data);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await api.updateProfile(profile);
      setProfile(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert(`Save error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const updatedProfile = await api.uploadResume(formData);
      setProfile(updatedProfile);
      alert("Resume parsed safely! Extracted skills and fields updated in profile.");
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  if (loading || !profile) {
    return <div className="p-12 text-center text-xs text-slate-400">Loading candidate profile...</div>;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Candidate Profile & Resume</h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure your technical skills, 2028 graduation timeline, preferences, and upload your resume
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-all cursor-pointer disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          <span>{saving ? "Saving Changes..." : "Save Profile"}</span>
        </button>
      </div>

      {saveSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />
          <span>Profile preferences saved successfully!</span>
        </div>
      )}

      {/* Resume Upload Card (Section 5) */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-indigo-400" />
            <h2 className="font-semibold text-sm text-white">Resume Document Parsing (PDF / DOCX)</h2>
          </div>
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Deterministic Parsing & Sandboxed Extraction</span>
          </span>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed">
          Upload your resume in PDF or DOCX format. The system extracts structured skills and experience without blind trust, allowing you to edit any fields below.
        </p>

        <div className="flex items-center gap-4">
          <label className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 cursor-pointer transition-colors">
            <Upload className={`h-4 w-4 ${uploading ? "animate-spin" : ""}`} />
            <span>{uploading ? "Extracting Content..." : "Upload PDF or DOCX Resume"}</span>
            <input
              type="file"
              accept=".pdf,.docx,.doc"
              onChange={handleResumeUpload}
              className="hidden"
            />
          </label>
          {profile.raw_resume_text && (
            <span className="text-xs text-emerald-400 flex items-center gap-1">
              ✓ Resume document parsed ({profile.raw_resume_text.length} chars)
            </span>
          )}
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Personal Details */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="font-semibold text-sm text-white flex items-center gap-2">
            <User className="h-4 w-4 text-cyan-400" />
            <span>Personal & Academic Details</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Full Name</label>
              <input
                type="text"
                value={profile.full_name || ""}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">University / College</label>
              <input
                type="text"
                value={profile.university || ""}
                onChange={(e) => setProfile({ ...profile, university: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Graduation Year</label>
              <input
                type="number"
                value={profile.graduation_year || 2028}
                onChange={(e) => setProfile({ ...profile, graduation_year: parseInt(e.target.value) || 2028 })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 font-bold text-indigo-400"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Degree</label>
              <input
                type="text"
                value={profile.degree || ""}
                onChange={(e) => setProfile({ ...profile, degree: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Current Location</label>
              <input
                type="text"
                value={profile.location || ""}
                onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Email Address</label>
              <input
                type="email"
                value={profile.email || ""}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">LinkedIn Profile URL</label>
              <input
                type="url"
                value={profile.linkedin_url || ""}
                onChange={(e) => setProfile({ ...profile, linkedin_url: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">GitHub Profile URL</label>
              <input
                type="url"
                value={profile.github_url || ""}
                onChange={(e) => setProfile({ ...profile, github_url: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Portfolio / Website URL</label>
              <input
                type="url"
                value={profile.portfolio_url || ""}
                onChange={(e) => setProfile({ ...profile, portfolio_url: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>
          </div>
        </div>

        {/* Technical Skills */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="font-semibold text-sm text-white flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <span>Technical Skills</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Programming Languages (comma separated)</label>
              <input
                type="text"
                value={(profile.skills?.languages || []).join(", ")}
                onChange={(e) => setProfile({
                  ...profile,
                  skills: { ...profile.skills, languages: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }
                })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Frameworks & Libraries (comma separated)</label>
              <input
                type="text"
                value={(profile.skills?.frameworks || []).join(", ")}
                onChange={(e) => setProfile({
                  ...profile,
                  skills: { ...profile.skills, frameworks: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }
                })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Databases (comma separated)</label>
              <input
                type="text"
                value={(profile.skills?.databases || []).join(", ")}
                onChange={(e) => setProfile({
                  ...profile,
                  skills: { ...profile.skills, databases: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }
                })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-medium">Cloud & Tools (comma separated)</label>
              <input
                type="text"
                value={(profile.skills?.tools || []).join(", ")}
                onChange={(e) => setProfile({
                  ...profile,
                  skills: { ...profile.skills, tools: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }
                })}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>
          </div>
        </div>

        {/* Featured Projects */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="font-semibold text-sm text-white flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-violet-400" />
            <span>Featured Engineering Projects</span>
          </h2>

          <div className="space-y-3">
            {(profile.experiences?.projects || []).map((proj: any, idx: number) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                <div className="font-semibold text-slate-200 text-xs">{proj.title}</div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{proj.description}</p>
                <div className="text-[10px] text-indigo-400">Tech: {(proj.technologies || []).join(", ")}</div>
              </div>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
}
