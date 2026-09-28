import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.opportunity import Company, Opportunity
from app.models.contact import Contact, ContactEvidence, OpportunityContact
from app.models.outreach import OutreachMessage, OutreachEvent
from app.models.application import Application
from app.models.followup import FollowUp
from app.core.security import get_password_hash

async def seed_database():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        existing_user = await db.execute(select(User).where(User.email == "demo.student2028@internreach.ai"))
        if existing_user.scalar_one_or_none():
            print("Database already seeded with demo data.")
            return

        print("Seeding database with realistic demo data for 2028 engineering intern...")

        # 1. Primary Demo User
        user = User(
            email="demo.student2028@internreach.ai",
            hashed_password=get_password_hash("Password123!"),
            full_name="Arjun Mehta (Demo Student)",
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        await db.flush()

        # 2. Candidate Profile
        profile = CandidateProfile(
            user_id=user.id,
            full_name=user.full_name,
            university="Indian Institute of Technology / BITS Pilani (Demo)",
            degree="B.Tech in Computer Science & Engineering",
            graduation_year=2028,
            current_year="Sophomore / 2nd Year",
            location="Bengaluru, India",
            preferred_locations=["Bengaluru", "Hyderabad", "Pune", "Delhi NCR", "Remote"],
            email=user.email,
            linkedin_url="https://linkedin.com/in/demo-arjun-2028",
            github_url="https://github.com/demo-arjun-dev",
            portfolio_url="https://demo-arjun-portfolio.vercel.app",
            target_roles=[
                "Software Engineering Intern",
                "SDE Intern",
                "Backend Engineering Intern",
                "Full Stack Engineering Intern",
                "AI/ML Engineering Intern",
                "Data Engineering Intern"
            ],
            target_industries=["Fintech", "Enterprise SaaS", "AI/ML", "Consumer Tech"],
            target_companies=["Razorpay", "CRED", "Swiggy", "Microsoft", "Postman", "Zomato", "PhonePe", "Zerodha", "Flipkart", "Uber"],
            preferred_company_sizes=["High-Growth Tech Startup", "Enterprise Scale"],
            preferred_internship_duration="2-6 months",
            remote_preference="Hybrid / Remote / On-site",
            skills={
                "languages": ["Python", "Golang", "TypeScript", "C++", "SQL"],
                "frameworks": ["FastAPI", "Next.js", "React", "Node.js", "Express"],
                "databases": ["PostgreSQL", "Redis", "MongoDB", "SQLite"],
                "cloud": ["AWS (S3, EC2, Lambda)", "Docker", "Git"],
                "ai_ml": ["PyTorch", "LangChain", "OpenAI/Claude API", "Transformers"],
                "tools": ["Linux", "Postman", "Docker Compose", "GitHub Actions"]
            },
            experiences={
                "internships": [],
                "projects": [
                    {
                        "title": "Distributed Asynchronous Job Dispatcher",
                        "description": "Engineered a low-latency task queue with async Python, Redis streams, and PostgreSQL worker state replication handling 10k mock tasks/sec.",
                        "technologies": ["Python", "FastAPI", "Redis", "PostgreSQL", "Docker"]
                    },
                    {
                        "title": "Agentic Technical Document Synthesizer",
                        "description": "Architected a multi-step RAG pipeline using LangChain, Claude API, and vector embeddings for semantic code repository querying.",
                        "technologies": ["Python", "LangChain", "Vector DB", "Next.js"]
                    },
                    {
                        "title": "High-Throughput In-Memory KV Store",
                        "description": "Created a lightweight concurrent key-value store in Golang with WAL persistence and LRU cache eviction.",
                        "technologies": ["Golang", "Concurrency", "Linux"]
                    }
                ],
                "research": [
                    {
                        "title": "Optimizing Vector Indexing in Distributed Systems",
                        "description": "Undergraduate research initiative exploring HNSW graph partition latency.",
                        "technologies": ["Python", "C++", "Vector Search"]
                    }
                ],
                "achievements": [
                    "Winner, National College Hackathon 2024 (1st place among 350 teams)",
                    "Codeforces Candidate Master / LeetCode Top 2%",
                    "Dean's Honor List for Academic Excellence"
                ],
                "leadership": [
                    "President, Open Source & Developers Club",
                    "Mentor for 1st-year computer science students"
                ],
                "certifications": [
                    "AWS Certified Cloud Practitioner (2024)",
                    "DeepLearning.AI Deep Learning Specialization"
                ]
            }
        )
        db.add(profile)
        await db.flush()

        # 3. 10 Companies (Clearly labeled DEMO DATA)
        company_specs = [
            ("Razorpay (Demo Data)", "razorpay.com", "Fintech / Payments", "1000-5000"),
            ("CRED (Demo Data)", "cred.club", "Fintech / Consumer", "500-1000"),
            ("Swiggy (Demo Data)", "swiggy.com", "Consumer Tech / Logistics", "5000+"),
            ("Microsoft India (Demo Data)", "microsoft.com", "Enterprise Cloud / Software", "10000+"),
            ("Postman (Demo Data)", "postman.com", "Developer Tools / SaaS", "500-1000"),
            ("Zomato (Demo Data)", "zomato.com", "Food Delivery & Logistics", "5000+"),
            ("PhonePe (Demo Data)", "phonepe.com", "Digital Payments / UPI", "1000-5000"),
            ("Zerodha (Demo Data)", "zerodha.com", "Fintech / Stock Broking", "500-1000"),
            ("Flipkart (Demo Data)", "flipkart.com", "E-commerce & Supply Chain", "10000+"),
            ("Uber India (Demo Data)", "uber.com", "Mobility & Platform Engineering", "5000+")
        ]
        created_companies = {}
        for name, domain, ind, sz in company_specs:
            c = Company(
                name=name,
                domain=domain,
                industry=ind,
                size=sz,
                careers_url=f"https://careers.{domain}/internships",
                description=f"{name} is a market-leading technology platform innovating in {ind}."
            )
            db.add(c)
            await db.flush()
            created_companies[name] = c

        # 4. 20 Opportunities (Clearly labeled DEMO DATA)
        opp_specs = [
            ("Razorpay (Demo Data)", "Software Engineering Intern - Payments Core (Demo)", "Bengaluru, India", "6 Months", 96.0, "2027/2028 Batch", ["Python", "Golang", "PostgreSQL", "REST APIs"], ["Kafka", "Docker"]),
            ("Razorpay (Demo Data)", "Backend Engineering Intern - Merchant Onboarding (Demo)", "Bengaluru, India", "6 Months", 92.0, "2028 Graduates", ["Python", "SQL", "FastAPI"], ["Redis", "AWS"]),
            ("CRED (Demo Data)", "Backend Engineering Intern - Platform Architecture (Demo)", "Bengaluru, India", "3-6 Months", 94.0, "2027 or 2028 Batch", ["Java", "Python", "SQL", "System Design"], ["Distributed Systems", "AWS"]),
            ("CRED (Demo Data)", "Data Engineering Intern - Realtime Processing (Demo)", "Bengaluru, India", "6 Months", 88.0, "2028 Graduates", ["Python", "SQL", "Spark"], ["Kafka", "Airflow"]),
            ("Swiggy (Demo Data)", "AI/ML Engineering Intern - Search & Discovery (Demo)", "Bengaluru, India / Hybrid", "6 Months", 95.0, "2028 Graduates eligible", ["Python", "PyTorch", "Machine Learning", "Transformers"], ["Vector DBs", "LangChain"]),
            ("Swiggy (Demo Data)", "Software Development Intern - Consumer App Backend (Demo)", "Bengaluru, India", "6 Months", 89.0, "2027/2028 Batch", ["Java", "Go", "SQL", "Microservices"], ["Docker", "Kubernetes"]),
            ("Microsoft India (Demo Data)", "SDE Intern - Azure Cloud Systems (Demo)", "Hyderabad, India", "2 Months (Summer)", 98.0, "2028 Bachelor's Candidates", ["C++", "C#", "Python", "Data Structures"], ["Cloud Systems", "Linux"]),
            ("Microsoft India (Demo Data)", "Research Intern - Foundations of AI (Demo)", "Bengaluru, India", "3-6 Months", 91.0, "2027/2028 Degree Students", ["Python", "PyTorch", "Math & Probability"], ["NLP", "Computer Vision"]),
            ("Postman (Demo Data)", "Full Stack Engineering Intern - Developer Experience (Demo)", "Bengaluru / Remote", "6 Months", 90.0, "2028 Undergraduate Candidates", ["TypeScript", "React", "Node.js", "REST APIs"], ["Next.js", "Docker"]),
            ("Postman (Demo Data)", "Systems Engineering Intern - API Runtime (Demo)", "Bengaluru, India", "6 Months", 87.0, "2028 Batch", ["Node.js", "C++", "Distributed Systems"], ["WebSockets", "Linux"]),
            ("Zomato (Demo Data)", "Data Engineering Intern - Realtime Analytics (Demo)", "Delhi NCR, India", "6 Months", 86.0, "2028 Batch Students", ["Python", "SQL", "Data Modeling"], ["Spark", "Snowflake"]),
            ("Zomato (Demo Data)", "Software Engineering Intern - Delivery Platform (Demo)", "Delhi NCR, India", "6 Months", 88.0, "2027/2028 Batch", ["Python", "Golang", "PostgreSQL"], ["Redis", "RabbitMQ"]),
            ("PhonePe (Demo Data)", "SDE Intern - Distributed Ledger & Ledgering (Demo)", "Bengaluru, India", "6 Months", 93.0, "2028 Batch", ["Java", "Python", "MySQL", "Algorithms"], ["Distributed Caches"]),
            ("PhonePe (Demo Data)", "Security Engineering Intern - AppSec (Demo)", "Bengaluru, India", "6 Months", 82.0, "2027/2028 Students", ["Python", "Network Security", "Linux"], ["OWASP", "Cryptography"]),
            ("Zerodha (Demo Data)", "Systems Engineering Intern - Low Latency Trading Systems (Demo)", "Bengaluru, India", "3-6 Months", 91.0, "2028 Graduates with Linux mastery", ["Python", "Go", "PostgreSQL", "Linux"], ["Redis", "C"]),
            ("Zerodha (Demo Data)", "Frontend Engineering Intern - Kite Web (Demo)", "Bengaluru, India / Remote", "3-6 Months", 85.0, "2028 Candidates", ["TypeScript", "Vue/React", "WebSockets"], ["CSS/Tailwind", "Canvas"]),
            ("Flipkart (Demo Data)", "SDE Intern - Supply Chain Optimization (Demo)", "Bengaluru, India", "2-6 Months", 90.0, "2028 Batch", ["Java", "Python", "Algorithms", "SQL"], ["Microservices", "Kafka"]),
            ("Flipkart (Demo Data)", "Data Science Intern - Catalog Intelligence (Demo)", "Bengaluru, India", "6 Months", 88.0, "2028 Batch", ["Python", "NLP", "Machine Learning"], ["Deep Learning", "GCP"]),
            ("Uber India (Demo Data)", "Software Engineering Intern - Rider Core (Demo)", "Hyderabad, India", "2-3 Months (Summer)", 94.0, "2028 Undergraduate Candidates", ["Go", "Java", "Python", "Data Structures"], ["Distributed Systems", "Kafka"]),
            ("Uber India (Demo Data)", "Infrastructure Engineering Intern - Cloud Fleet (Demo)", "Bengaluru, India", "3-6 Months", 89.0, "2028 Engineering Students", ["Python", "Go", "Docker", "Linux"], ["Kubernetes", "Observability"])
        ]

        created_opps = []
        for comp_name, title, loc, dur, conf, grad_req, req_s, pref_s in opp_specs:
            company = created_companies.get(comp_name)
            opp = Opportunity(
                company_id=company.id if company else None,
                company_name=comp_name,
                title=title,
                job_description=f"We are hiring a passionate engineering intern for {title}. You will design, build, and optimize high-throughput distributed systems in {loc}. Must have strong algorithmic skills and familiarity with {', '.join(req_s)}. Open to {grad_req}.",
                location=loc,
                internship_duration=dur,
                application_url=f"https://careers.{company.domain if company else 'demo.com'}/jobs/demo-{len(created_opps)+1}",
                source="public_careers_page",
                date_discovered=datetime.now(timezone.utc) - timedelta(days=len(created_opps) % 10),
                deadline=datetime.now(timezone.utc) + timedelta(days=30 + (len(created_opps) % 15)),
                graduation_eligibility=grad_req,
                required_skills=req_s,
                preferred_skills=pref_s,
                employment_type="Internship",
                evidence_url=f"https://careers.{company.domain if company else 'demo.com'}/jobs/demo-{len(created_opps)+1}",
                verified=True,
                eligibility_status="eligible",
                verification_confidence=conf / 100.0,
                verification_reasons=[
                    "Confirmed software/engineering internship posting",
                    f"Compatible graduation requirement: {grad_req}",
                    f"Location verified in {loc}"
                ],
                is_active=True
            )
            db.add(opp)
            await db.flush()
            created_opps.append(opp)

        # 5. 15 Realistic Recruiting Contacts (Clearly labeled DEMO DATA)
        contact_specs = [
            ("Razorpay (Demo Data)", "Ananya Sharma (Demo Recruiter)", "Lead University & Early Careers Talent Partner", "high", 0.96, "Directly leads campus and early talent cohorts at Razorpay."),
            ("Razorpay (Demo Data)", "Karthik Menon (Demo Recruiter)", "Technical Recruiter - Core Platform", "high", 0.90, "Technical recruiter sourcing backend and distributed systems interns."),
            ("CRED (Demo Data)", "Rohan Deshmukh (Demo Recruiter)", "Early Careers Talent Specialist", "high", 0.95, "Leads undergraduate engineering campus recruitment at CRED."),
            ("CRED (Demo Data)", "Aditi Rao (Demo Recruiter)", "Lead Technical Sourcer", "medium", 0.85, "Technical sourcer for engineering teams."),
            ("Swiggy (Demo Data)", "Priya Nair (Demo Recruiter)", "University Recruiter - AI & Data Labs", "high", 0.97, "Recruiter partnering with universities for AI/ML research internships."),
            ("Swiggy (Demo Data)", "Rahul Verma (Demo Recruiter)", "Talent Acquisition Manager - Tech", "medium", 0.82, "Leads engineering hiring at Swiggy."),
            ("Microsoft India (Demo Data)", "Vikas Agarwal (Demo Recruiter)", "University Recruiting Lead - India IDC", "high", 0.98, "Coordinates student hiring for Microsoft India Development Center."),
            ("Microsoft India (Demo Data)", "Meera Krishnan (Demo Recruiter)", "Senior Technical Recruiter - Azure", "high", 0.92, "Technical recruiter for Azure cloud platform teams."),
            ("Postman (Demo Data)", "Sneha Roy (Demo Recruiter)", "Technical Talent Partner - DevEx", "high", 0.91, "Focuses on developer tools and developer experience team recruiting."),
            ("Zomato (Demo Data)", "Tarun Sen (Demo Recruiter)", "Campus Talent Specialist", "high", 0.93, "Manages engineering intern cohorts at Zomato."),
            ("PhonePe (Demo Data)", "Deepak Joshi (Demo Recruiter)", "Early Careers Recruiting Lead", "high", 0.94, "Leads campus relationships and technical evaluations at PhonePe."),
            ("Zerodha (Demo Data)", "Kailash Nadh (Demo CTO)", "Chief Technology Officer", "medium", 0.80, "Engineering leader at Zerodha open to developer discussions and advice."),
            ("Flipkart (Demo Data)", "Sanjay Gupta (Demo Recruiter)", "Senior Manager - University Relations", "high", 0.95, "Leads Flipkart's campus outreach and tech student challenges."),
            ("Flipkart (Demo Data)", "Neha Bajaj (Demo Recruiter)", "Technical Recruiter - Supply Chain Tech", "high", 0.89, "Recruiter for logistics and supply chain systems engineering."),
            ("Uber India (Demo Data)", "Sameer Kulkarni (Demo Recruiter)", "Lead Technical Recruiter - India Tech Centers", "high", 0.94, "Focuses on undergraduate and graduate software engineering interns.")
        ]

        created_contacts = []
        for comp_name, name, title, rel_op, rel_sc, reason in contact_specs:
            company = created_companies.get(comp_name)
            c = Contact(
                company_id=company.id if company else None,
                company_name=comp_name,
                name=name,
                current_title=title,
                public_profile_url=f"https://linkedin.com/in/{name.lower().replace(' ', '-').replace('(', '').replace(')', '')}",
                linkedin_url=f"https://linkedin.com/in/{name.lower().replace(' ', '-').replace('(', '').replace(')', '')}",
                source="public_university_relations",
                operational_relevance=rel_op,
                relevance_score=rel_sc,
                confidence=0.95,
                relevance_reason=reason,
                verified_at=datetime.now(timezone.utc)
            )
            db.add(c)
            await db.flush()

            # Add Evidence
            ev = ContactEvidence(
                contact_id=c.id,
                source_type="public_careers_portal",
                source_url=f"https://linkedin.com/company/{company.domain if company else 'demo'}",
                snippet=f"Publicly confirmed in role: {title} at {comp_name}. {reason}",
                confidence=0.95
            )
            db.add(ev)

            # Link to first matching opportunity of company
            matching_opp = next((o for o in created_opps if o.company_name == comp_name), None)
            if matching_opp:
                opp_link = OpportunityContact(
                    opportunity_id=matching_opp.id,
                    contact_id=c.id,
                    relevance_notes=reason
                )
                db.add(opp_link)

            created_contacts.append(c)

        # 6. 10 Outreach Messages (Clear statuses across CRM workflow)
        outreach_specs = [
            (created_contacts[0], created_opps[0], "APPROVED", "LINKEDIN_CONNECT", "RECRUITER", "Hi Ananya, I noticed Razorpay's Core Payments internship. As a 2028 engineering student with experience building distributed async Python/FastAPI services, I would appreciate any guidance on the application process. Thank you!"),
            (created_contacts[1], created_opps[1], "DRAFT", "LINKEDIN_CONNECT", "RECRUITER", "Hi Karthik, I saw your work hiring for Core Platform at Razorpay. As a 2028 engineering graduate focused on backend microservices and PostgreSQL, could you advise if sophomore applicants are eligible for this cycle?"),
            (created_contacts[2], created_opps[2], "SENT", "LINKEDIN_MESSAGE", "RECRUITER", "Hi Rohan, I saw CRED's Platform Engineering internship. As a 2028 undergraduate engineering student working on high-throughput queues and caching systems, I would love to learn more about the team's engineering stack."),
            (created_contacts[4], created_opps[4], "APPROVED", "LINKEDIN_CONNECT", "RECRUITER", "Hi Priya, I came across Swiggy's AI/ML internship. As a 2028 engineering student with project experience in PyTorch and vector search pipelines, I would appreciate your guidance on early-career roles."),
            (created_contacts[6], created_opps[6], "SENT", "LINKEDIN_MESSAGE", "RECRUITER", "Hi Vikas, I am an engineering student graduating in 2028 with background in C++ and systems programming. I wanted to inquire about the Azure Cloud SDE internship at Microsoft IDC. Thank you for your time!"),
            (created_contacts[8], created_opps[8], "DRAFT", "EMAIL", "RECRUITER", "Hi Sneha, I saw Postman's Full Stack DevEx internship. As a 2028 engineering graduate with Next.js and API tooling projects, I would appreciate any pointers regarding candidate expectations."),
            (created_contacts[9], created_opps[10], "REPLIED", "LINKEDIN_CONNECT", "RECRUITER", "Hi Tarun, I noticed Zomato's Realtime Data Engineering internship. As a 2028 student with strong SQL and data modeling skills, I'd value any advice on the hiring timeline."),
            (created_contacts[10], created_opps[12], "POSITIVE", "LINKEDIN_CONNECT", "RECRUITER", "Hi Deepak, following PhonePe's high-scale fintech infrastructure work, I wanted to inquire about 2028 graduate internship opportunities in backend systems."),
            (created_contacts[11], created_opps[14], "SENT", "EMAIL", "EMPLOYEE", "Hi Kailash, I greatly appreciate Zerodha's engineering blogs on minimalist architectures. As a 2028 student passionate about Linux systems and low latency, I would value your perspective on early career development."),
            (created_contacts[14], created_opps[18], "FOLLOW_UP_DUE", "LINKEDIN_CONNECT", "RECRUITER", "Hi Sameer, I am reaching out regarding Uber's Rider Core SDE internship. As a 2028 engineering undergraduate with Golang and distributed systems projects, I'd love to connect.")
        ]

        created_outreach = []
        for contact, opp, status_str, channel, strat, content in outreach_specs:
            msg = OutreachMessage(
                user_id=user.id,
                opportunity_id=opp.id if opp else None,
                contact_id=contact.id,
                channel=channel,
                strategy=strat,
                subject=f"Internship Inquiry - Arjun Mehta (2028 Grad)",
                content=content,
                personalization_reason="Personalized message referencing candidate's 2028 graduation year, matched backend/AI skills, and respectful inquiry.",
                evidence_used=["Public verified recruiting role", "Public careers listing"],
                confidence=0.94,
                status=status_str,
                approved_at=datetime.now(timezone.utc) if status_str in ("APPROVED", "SENT", "REPLIED", "POSITIVE") else None,
                approved_by=user.id if status_str in ("APPROVED", "SENT", "REPLIED", "POSITIVE") else None,
                sent_at=datetime.now(timezone.utc) - timedelta(days=8) if status_str in ("SENT", "REPLIED", "POSITIVE", "FOLLOW_UP_DUE") else None,
                last_contacted_at=datetime.now(timezone.utc) - timedelta(days=8) if status_str in ("SENT", "REPLIED", "POSITIVE", "FOLLOW_UP_DUE") else None,
                message_version=1,
                model_name="mock_provider",
                prompt_version="v1.0"
            )
            db.add(msg)
            await db.flush()

            # Follow-up for the FOLLOW_UP_DUE item
            if status_str == "FOLLOW_UP_DUE":
                fu = FollowUp(
                    outreach_id=msg.id,
                    user_id=user.id,
                    sequence_number=1,
                    wait_days=7,
                    due_date=datetime.now(timezone.utc) - timedelta(days=1),
                    status="DUE",
                    content="Hi Sameer, following up on my previous note. Wanted to check if your team is currently reviewing 2028 undergraduate engineering applications for the internship role. Thanks!"
                )
                db.add(fu)

            created_outreach.append(msg)

        # 7. 10 Tracked Applications
        app_specs = [
            ("Razorpay (Demo Data)", "Software Engineering Intern - Payments Core (Demo)", "APPLIED", created_opps[0].id, created_contacts[0].id, "Technical screening scheduled"),
            ("CRED (Demo Data)", "Backend Engineering Intern - Platform Architecture (Demo)", "OA", created_opps[2].id, created_contacts[2].id, "Completed online coding assessment"),
            ("Swiggy (Demo Data)", "AI/ML Engineering Intern - Search & Discovery (Demo)", "INTERVIEW", created_opps[4].id, created_contacts[4].id, "Technical round with ML engineering manager on Monday"),
            ("Microsoft India (Demo Data)", "SDE Intern - Azure Cloud Systems (Demo)", "APPLIED", created_opps[6].id, created_contacts[6].id, "Submitted via careers portal with referral"),
            ("Postman (Demo Data)", "Full Stack Engineering Intern (Demo)", "SAVED", created_opps[8].id, created_contacts[8].id, "Preparing portfolio link"),
            ("Zomato (Demo Data)", "Data Engineering Intern (Demo)", "OA", created_opps[10].id, created_contacts[9].id, "Awaiting test results"),
            ("PhonePe (Demo Data)", "SDE Intern - Distributed Ledger (Demo)", "FINAL_ROUND", created_opps[12].id, created_contacts[10].id, "Final hiring manager conversation scheduled"),
            ("Zerodha (Demo Data)", "Systems Engineering Intern (Demo)", "SAVED", created_opps[14].id, created_contacts[11].id, "Reading tech documentation"),
            ("Flipkart (Demo Data)", "SDE Intern - Supply Chain (Demo)", "APPLIED", created_opps[16].id, created_contacts[12].id, "Application under review"),
            ("Uber India (Demo Data)", "Software Engineering Intern - Rider Core (Demo)", "APPLIED", created_opps[18].id, created_contacts[14].id, "Recruiter screening call completed")
        ]

        for comp, role, st, opp_id, cont_id, note in app_specs:
            appl = Application(
                user_id=user.id,
                opportunity_id=opp_id,
                company_name=comp,
                role_title=role,
                application_url=f"https://careers.example.com/apply/demo",
                date_applied=datetime.now(timezone.utc) - timedelta(days=5),
                status=st,
                recruiter_contact_id=cont_id,
                interview_stage="Round 1 / Evaluation",
                next_action=note,
                notes=note
            )
            db.add(appl)

        await db.commit()
        print("Database seeded successfully with 10 companies, 20 opportunities, 15 contacts, 10 messages, and 10 applications.")

if __name__ == "__main__":
    asyncio.run(seed_database())
