import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";

export const metadata: Metadata = {
  title: "InternReach AI — AI Recruiter Research & Outreach CRM",
  description: "AI-assisted internship discovery, recruiter research, and personalized outreach CRM for 2028 engineering undergraduates.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full bg-[#090D16]">
      <body className="min-h-full flex flex-col text-slate-100 bg-[#090D16]">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#090D16]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
