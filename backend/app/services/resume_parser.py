import io
import re
from typing import Dict, Any, Tuple
import pypdf
import docx
from app.utils.sanitizer import validate_file_mime_and_size
from app.utils.prompt_guard import sanitize_external_text

COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "C++", "Java", "Go", "Golang", "Rust", "SQL",
    "FastAPI", "Django", "Flask", "React", "Next.js", "Node.js", "Express", "Tailwind CSS",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Linux", "Git", "CI/CD",
    "PyTorch", "TensorFlow", "Scikit-Learn", "LangChain", "OpenAI", "Claude", "LLMs", "RAG", "Transformers"
]

def extract_text_from_pdf(content: bytes) -> str:
    """Extracts raw text safely from PDF bytes using pypdf."""
    reader = pypdf.PdfReader(io.BytesIO(content))
    extracted = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted.append(text)
    return "\n".join(extracted)

def extract_text_from_docx(content: bytes) -> str:
    """Extracts raw text safely from DOCX bytes using python-docx."""
    doc = docx.Document(io.BytesIO(content))
    extracted = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(extracted)

def parse_resume_document(filename: str, content: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Safely validates and extracts text, then derives structured profile data.
    Never executes embedded code. Sanitizes text against prompt injection.
    """
    valid, err = validate_file_mime_and_size(filename, content)
    if not valid:
        raise ValueError(err)

    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        raw_text = extract_text_from_pdf(content)
    elif ext in ("docx", "doc"):
        raw_text = extract_text_from_docx(content)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    sanitized_text, injection_detected = sanitize_external_text(raw_text)

    # Deterministic extraction of skills and basics (avoiding blind LLM hallucination)
    detected_skills = []
    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, sanitized_text, re.IGNORECASE):
            detected_skills.append(skill)

    # Extract potential graduation year
    grad_year = 2028 # default target
    grad_match = re.search(r"\b(202[4-9]|203[0-2])\b", sanitized_text)
    if grad_match:
        found_year = int(grad_match.group(1))
        if 2025 <= found_year <= 2030:
            grad_year = found_year

    # Extract email and links
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", sanitized_text)
    email = email_match.group(0) if email_match else None

    github_match = re.search(r"https?://(www\.)?github\.com/[A-Za-z0-9_-]+", sanitized_text)
    github_url = github_match.group(0) if github_match else None

    linkedin_match = re.search(r"https?://(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", sanitized_text)
    linkedin_url = linkedin_match.group(0) if linkedin_match else None

    structured_data = {
        "detected_skills": detected_skills,
        "graduation_year": grad_year,
        "email": email,
        "github_url": github_url,
        "linkedin_url": linkedin_url,
        "prompt_injection_flagged": injection_detected,
        "word_count": len(sanitized_text.split())
    }

    return sanitized_text, structured_data
