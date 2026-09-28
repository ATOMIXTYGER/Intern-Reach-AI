from typing import List, Dict, Any
from app.providers.search.base import SearchProvider

DEMO_OPPORTUNITIES = [
    {
        "company_name": "Razorpay (Demo Data)",
        "title": "Software Engineering Intern - Payments Core (Demo)",
        "job_description": "Join Razorpay's high-scale Core Payments engineering team. You will build high-throughput microservices using Golang/Python, participate in system design reviews, and build resilient distributed transaction pipelines. Requirements: Pursuing B.Tech/B.E in Computer Science or related engineering field graduating in 2027 or 2028. Proficiency in data structures, algorithms, and SQL.",
        "location": "Bengaluru, India",
        "internship_duration": "6 Months (Jan-June or Summer)",
        "application_url": "https://careers.razorpay.com/jobs/demo-swe-intern-2026",
        "source": "public_careers_page",
        "graduation_eligibility": "2027 or 2028 Graduates",
        "required_skills": ["Python", "Golang", "Data Structures", "PostgreSQL", "REST APIs"],
        "preferred_skills": ["Kafka", "Docker", "Redis"],
        "employment_type": "Internship",
        "evidence_url": "https://careers.razorpay.com/jobs/demo-swe-intern-2026"
    },
    {
        "company_name": "CRED (Demo Data)",
        "title": "Backend Engineering Intern - Platform (Demo)",
        "job_description": "We are seeking high-caliber undergraduate engineering students for our Platform Engineering team. You will work on distributed caches, low-latency API gateways, and asynchronous event consumers. Candidates graduating in 2028 with proven software project experience and curiosity are welcome to apply.",
        "location": "Bengaluru, India",
        "internship_duration": "3-6 Months",
        "application_url": "https://careers.cred.club/demo-backend-intern",
        "source": "public_careers_page",
        "graduation_eligibility": "2027 or 2028 Graduates",
        "required_skills": ["Java", "Python", "System Design Basics", "SQL"],
        "preferred_skills": ["Distributed Systems", "AWS", "Microservices"],
        "employment_type": "Internship",
        "evidence_url": "https://careers.cred.club/demo-backend-intern"
    },
    {
        "company_name": "Swiggy (Demo Data)",
        "title": "AI/ML Engineering Intern - Search & Discovery (Demo)",
        "job_description": "Swiggy is looking for an AI/ML intern to help build semantic search, LLM-powered recommendations, and ranking models. Ideal candidates have coursework or project experience in Machine Learning, PyTorch/TensorFlow, and vector databases. 2028 undergraduate engineering students with competitive programming or research exposure encouraged.",
        "location": "Bengaluru, India / Hybrid",
        "internship_duration": "6 Months",
        "application_url": "https://careers.swiggy.com/demo-ai-intern",
        "source": "public_careers_page",
        "graduation_eligibility": "2028 Graduates eligible",
        "required_skills": ["Python", "PyTorch", "Machine Learning", "Transformers", "SQL"],
        "preferred_skills": ["Vector DBs", "LangChain", "FastAPI"],
        "employment_type": "Internship",
        "evidence_url": "https://careers.swiggy.com/demo-ai-intern"
    },
    {
        "company_name": "Microsoft India (Demo Data)",
        "title": "Software Development Engineer Intern - Azure Cloud (Demo)",
        "job_description": "Microsoft is seeking undergraduate students currently enrolled in a bachelor's degree program with graduation expected in 2028. You will collaborate on core Azure cloud infrastructure, distributed storage components, and cross-platform tooling.",
        "location": "Hyderabad, India",
        "internship_duration": "2 Months (Summer)",
        "application_url": "https://careers.microsoft.com/students/demo-swe-2026",
        "source": "public_university_portal",
        "graduation_eligibility": "2028 Bachelor's Degree Graduates",
        "required_skills": ["C++", "C#", "Python", "Data Structures", "Algorithms"],
        "preferred_skills": ["Cloud Architecture", "Linux", "Git"],
        "employment_type": "Internship",
        "evidence_url": "https://careers.microsoft.com/students/demo-swe-2026"
    },
    {
        "company_name": "Postman (Demo Data)",
        "title": "Full Stack Engineering Intern - Developer Experience (Demo)",
        "job_description": "Work with Postman's DevEx and API tooling teams. You will contribute to Next.js/React interfaces, Node.js API services, and WebSocket communication channels. Looking for ambitious 2028 engineering students with strong JS/TS and web fundamentals.",
        "location": "Bengaluru, India / Remote",
        "internship_duration": "6 Months",
        "application_url": "https://postman.com/careers/demo-fullstack-intern",
        "source": "public_careers_page",
        "graduation_eligibility": "2028 Undergraduate Candidates",
        "required_skills": ["TypeScript", "React", "Node.js", "REST APIs"],
        "preferred_skills": ["Tailwind CSS", "Next.js", "Docker"],
        "employment_type": "Internship",
        "evidence_url": "https://postman.com/careers/demo-fullstack-intern"
    },
    {
        "company_name": "Zomato (Demo Data)",
        "title": "Data Engineering Intern - Real-time Analytics (Demo)",
        "job_description": "Zomato is hiring a Data Engineering intern to build Spark pipelines, Kafka stream processing, and analytics data models. Open to 2028 engineering batch students with strong SQL, Python, and analytical mindset.",
        "location": "Delhi NCR (Gurugram), India",
        "internship_duration": "6 Months",
        "application_url": "https://zomato.com/careers/demo-data-intern",
        "source": "public_careers_page",
        "graduation_eligibility": "2028 Batch Students",
        "required_skills": ["Python", "SQL", "Data Modeling", "Apache Spark"],
        "preferred_skills": ["Kafka", "Snowflake", "dbt"],
        "employment_type": "Internship",
        "evidence_url": "https://zomato.com/careers/demo-data-intern"
    }
]

DEMO_CONTACTS_BY_COMPANY = {
    "Razorpay (Demo Data)": [
        {
            "name": "Ananya Sharma (Demo Recruiter)",
            "company_name": "Razorpay (Demo Data)",
            "current_title": "Lead University & Early Careers Talent Partner",
            "public_profile_url": "https://linkedin.com/in/demo-ananya-recruiter-razorpay",
            "source": "public_university_relations",
            "operational_relevance": "high",
            "relevance_score": 0.95,
            "confidence": 0.96,
            "relevance_reason": "Directly oversees campus and university internship hiring programs across engineering.",
            "snippet": "University Talent Partner at Razorpay. Spearheading student hiring, engineering internship cohorts, and tech university alliances."
        },
        {
            "name": "Karthik Menon (Demo Recruiter)",
            "company_name": "Razorpay (Demo Data)",
            "current_title": "Technical Recruiter - Core Engineering",
            "public_profile_url": "https://linkedin.com/in/demo-karthik-recruiter-razorpay",
            "source": "public_talent_directory",
            "operational_relevance": "high",
            "relevance_score": 0.88,
            "confidence": 0.90,
            "relevance_reason": "Technical recruiter hiring for backend and distributed systems engineering.",
            "snippet": "Technical Recruiter at Razorpay focusing on high-scale backend systems, distributed architectures, and SDE talent."
        }
    ],
    "CRED (Demo Data)": [
        {
            "name": "Rohan Deshmukh (Demo Recruiter)",
            "company_name": "CRED (Demo Data)",
            "current_title": "Early Careers Talent Specialist",
            "public_profile_url": "https://linkedin.com/in/demo-rohan-recruiter-cred",
            "source": "public_university_relations",
            "operational_relevance": "high",
            "relevance_score": 0.94,
            "confidence": 0.95,
            "relevance_reason": "Dedicated campus recruiter leading CRED's 2026/2027/2028 undergraduate engineering internships.",
            "snippet": "Early Careers Talent Specialist at CRED. Building the next generation of product and backend engineering leaders."
        }
    ],
    "Swiggy (Demo Data)": [
        {
            "name": "Priya Nair (Demo Recruiter)",
            "company_name": "Swiggy (Demo Data)",
            "current_title": "University Recruiter - AI & Data Labs",
            "public_profile_url": "https://linkedin.com/in/demo-priya-recruiter-swiggy",
            "source": "public_careers_portal",
            "operational_relevance": "high",
            "relevance_score": 0.96,
            "confidence": 0.97,
            "relevance_reason": "Coordinates campus research and internship programs specifically for AI/ML and Data Science teams.",
            "snippet": "University Recruiter at Swiggy partnering with top engineering campuses for AI/ML research internships."
        }
    ],
    "Microsoft India (Demo Data)": [
        {
            "name": "Vikas Agarwal (Demo Recruiter)",
            "company_name": "Microsoft India (Demo Data)",
            "current_title": "University Recruiting Lead - India IDC",
            "public_profile_url": "https://linkedin.com/in/demo-vikas-recruiter-msft",
            "source": "public_campus_relations",
            "operational_relevance": "high",
            "relevance_score": 0.98,
            "confidence": 0.98,
            "relevance_reason": "Leads Microsoft India university recruiting for undergraduate SDE intern cohorts across IDC Hyderabad/Bengaluru.",
            "snippet": "University Recruiting Lead at Microsoft India. Empowering students and 2028 future tech leaders to achieve more."
        }
    ],
    "Postman (Demo Data)": [
        {
            "name": "Sneha Roy (Demo Recruiter)",
            "company_name": "Postman (Demo Data)",
            "current_title": "Technical Talent Partner - DevEx",
            "public_profile_url": "https://linkedin.com/in/demo-sneha-recruiter-postman",
            "source": "public_careers_page",
            "operational_relevance": "high",
            "relevance_score": 0.90,
            "confidence": 0.92,
            "relevance_reason": "Recruiter responsible for developer experience, web platform, and student programs at Postman.",
            "snippet": "Technical Recruiter at Postman passionate about hiring top-tier full stack and API developers."
        }
    ]
}

class MockSearchProvider(SearchProvider):
    provider_name: str = "mock"

    async def search_opportunities(
        self,
        roles: List[str] = None,
        locations: List[str] = None,
        companies: List[str] = None,
        keywords: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        results = []
        for opp in DEMO_OPPORTUNITIES:
            # Filter if companies specified
            if companies:
                matches_company = any(c.lower() in opp["company_name"].lower() for c in companies)
                if not matches_company:
                    continue
            results.append(opp)
            if len(results) >= limit:
                break
        return results if results else DEMO_OPPORTUNITIES[:limit]

    async def search_contacts(
        self,
        company_name: str,
        target_roles: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        # Match company
        for comp_key, contacts in DEMO_CONTACTS_BY_COMPANY.items():
            if comp_key.lower().startswith(company_name.lower().split()[0]):
                return contacts[:limit]
        
        # Generic fallback contact for demo
        clean_name = company_name.replace("(Demo Data)", "").strip()
        return [
            {
                "name": f"Campus Talent Partner (Demo)",
                "company_name": company_name,
                "current_title": "University & Early Careers Recruiting",
                "public_profile_url": f"https://linkedin.com/company/{clean_name.lower()}-demo",
                "source": "public_careers_portal",
                "operational_relevance": "high",
                "relevance_score": 0.90,
                "confidence": 0.92,
                "relevance_reason": f"Recruiting team member responsible for university student outreach at {clean_name}.",
                "snippet": f"Early careers recruiting contact representing engineering campus hiring at {company_name}."
            }
        ]
