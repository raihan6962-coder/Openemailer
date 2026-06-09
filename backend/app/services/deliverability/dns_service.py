from typing import Optional, Dict, List
import dns.resolver
import dns.query
import re
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.deliverability import DNSCheckRepository
from app.repositories.domain import DomainRepository


class DNSService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dns_check_repo = DNSCheckRepository(db)
        self.domain_repo = DomainRepository(db)

    async def check_spf(self, domain: str) -> Dict:
        result = {"status": "fail", "record": None, "issues": []}
        try:
            answers = dns.resolver.resolve(domain, "TXT")
            for rdata in answers:
                txt = str(rdata).strip('"').strip("'")
                if txt.startswith("v=spf1"):
                    result["status"] = "pass"
                    result["record"] = txt
                    break
            if result["status"] == "fail":
                result["issues"].append("No SPF record found")
        except Exception as e:
            result["issues"].append(str(e))
        return result

    async def check_dkim(self, domain: str, selector: str = "default") -> Dict:
        result = {"status": "fail", "record": None, "issues": []}
        try:
            dkim_domain = f"{selector}._domainkey.{domain}"
            answers = dns.resolver.resolve(dkim_domain, "TXT")
            for rdata in answers:
                txt = str(rdata).strip('"').strip("'")
                if txt.startswith("v=DKIM1"):
                    result["status"] = "pass"
                    result["record"] = txt
                    break
            if result["status"] == "fail":
                result["issues"].append("No DKIM record found")
        except Exception as e:
            result["issues"].append(str(e))
        return result

    async def check_dmarc(self, domain: str) -> Dict:
        result = {"status": "fail", "record": None, "issues": []}
        try:
            dmarc_domain = f"_dmarc.{domain}"
            answers = dns.resolver.resolve(dmarc_domain, "TXT")
            for rdata in answers:
                txt = str(rdata).strip('"').strip("'")
                if txt.startswith("v=DMARC1"):
                    result["status"] = "pass"
                    result["record"] = txt
                    break
            if result["status"] == "fail":
                result["issues"].append("No DMARC record found")
        except Exception as e:
            result["issues"].append(str(e))
        return result

    async def check_mx(self, domain: str) -> Dict:
        result = {"status": "fail", "records": [], "issues": []}
        try:
            answers = dns.resolver.resolve(domain, "MX")
            for rdata in answers:
                result["records"].append(str(rdata.exchange))
            if result["records"]:
                result["status"] = "pass"
            else:
                result["issues"].append("No MX records found")
        except Exception as e:
            result["issues"].append(str(e))
        return result

    async def full_dns_check(self, domain: str, workspace_id: str) -> Dict:
        spf = await self.check_spf(domain)
        dkim = await self.check_dkim(domain)
        dmarc = await self.check_dmarc(domain)
        mx = await self.check_mx(domain)

        overall_issues = spf.get("issues", []) + dkim.get("issues", []) + dmarc.get("issues", []) + mx.get("issues", [])
        passed = sum(1 for r in [spf, dkim, dmarc, mx] if r["status"] == "pass")
        overall_health = "healthy" if passed >= 3 else "warning" if passed >= 1 else "critical"

        check = await self.dns_check_repo.create(
            workspace_id=workspace_id,
            domain=domain,
            spf_status=spf["status"],
            spf_record=spf.get("record"),
            dkim_status=dkim["status"],
            dkim_record=dkim.get("record"),
            dmarc_status=dmarc["status"],
            dmarc_record=dmarc.get("record"),
            mx_status=mx["status"],
            mx_records=", ".join(mx.get("records", [])),
            overall_health=overall_health,
            issues=overall_issues if overall_issues else None,
        )

        return {
            "domain": domain,
            "overall_health": overall_health,
            "checks": {"spf": spf, "dkim": dkim, "dmarc": dmarc, "mx": mx},
            "score": passed * 25,
        }
