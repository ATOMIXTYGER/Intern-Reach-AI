import httpx
from typing import List, Dict, Any
from app.providers.search.base import SearchProvider
from app.core.config import settings
from app.utils.ssrf import is_safe_url

class TavilySearchProvider(SearchProvider):
    provider_name: str = "tavily"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.SEARCH_PROVIDER_API_KEY

    async def search_opportunities(
        self,
        roles: List[str],
        locations: List[str],
        companies: List[str] = None,
        keywords: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        query_parts = []
        if roles:
            query_parts.append(f'({" OR ".join(roles[:3])})')
        query_parts.append("internship 2026")
        if locations:
            query_parts.append(f'({" OR ".join(locations[:3])})')
        if companies:
            query_parts.append(f'({" OR ".join(companies[:3])})')
        if keywords:
            query_parts.append(keywords)
            
        query = " ".join(query_parts)

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_domains": ["careers.*", "lever.co", "greenhouse.io", "workday.com", "ashbyhq.com"],
            "max_results": limit
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.tavily.com/search", json=payload)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            url = item.get("url", "")
            safe, _ = is_safe_url(url)
            if not safe:
                continue

            results.append({
                "title": item.get("title", ""),
                "job_description": item.get("content", ""),
                "company_name": item.get("domain", "Unknown Company").split(".")[0].capitalize(),
                "location": locations[0] if locations else "Remote",
                "application_url": url,
                "source": "tavily_search",
                "evidence_url": url
            })
        return results

    async def search_contacts(
        self,
        company_name: str,
        target_roles: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        query = f'"{company_name}" ("University Recruiter" OR "Campus Recruiter" OR "Early Careers" OR "Talent Partner")'
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": limit
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.tavily.com/search", json=payload)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "name": item.get("title", "").split("-")[0].strip(),
                "company_name": company_name,
                "current_title": "Early Careers Talent Acquisition",
                "public_profile_url": item.get("url", ""),
                "source": "tavily_public_search",
                "snippet": item.get("content", "")
            })
        return results
