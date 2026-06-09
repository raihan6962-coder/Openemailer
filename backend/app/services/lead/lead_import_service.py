import pandas as pd
import re
import io
from typing import List, Dict
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.lead import LeadRepository, LeadListRepository


class LeadImportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.list_repo = LeadListRepository(db)

    def detect_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        field_map = {}
        col_lower = {c: c.lower().strip() for c in df.columns}

        field_patterns = {
            "email": [r"email", r"e-mail", r"mail"],
            "first_name": [r"first.?name", r"fname", r"first"],
            "last_name": [r"last.?name", r"lname", r"last"],
            "full_name": [r"full.?name", r"name"],
            "company": [r"company", r"organization", r"org", r"business"],
            "website": [r"website", r"web", r"url", r"site", r"domain"],
            "country": [r"country", r"nation"],
            "phone": [r"phone", r"telephone", r"mobile", r"cell"],
            "industry": [r"industry", r"sector"],
            "job_title": [r"job.?title", r"title", r"position", r"role"],
            "linkedin_url": [r"linkedin", r"linked.?in"],
        }

        for field, patterns in field_patterns.items():
            for pattern in patterns:
                for col, lower in col_lower.items():
                    if re.search(pattern, lower):
                        field_map[field] = col
                        break
                if field in field_map:
                    break

        return field_map

    async def import_csv(self, file: UploadFile, workspace_id: UUID) -> dict:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        return await self._import_dataframe(df, workspace_id, "csv")

    async def import_xlsx(self, file: UploadFile, workspace_id: UUID) -> dict:
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        return await self._import_dataframe(df, workspace_id, "xlsx")

    async def _import_dataframe(self, df: pd.DataFrame, workspace_id: UUID, source: str) -> dict:
        field_map = self.detect_fields(df)
        imported = 0
        duplicates = 0
        invalid = 0

        for _, row in df.iterrows():
            email = str(row.get(field_map.get("email", "email"), "")).strip().lower()
            if not email or "@" not in email:
                invalid += 1
                continue

            existing = await self.lead_repo.get_by_email(email, workspace_id)
            if existing:
                duplicates += 1
                continue

            await self.lead_repo.create(
                workspace_id=workspace_id,
                email=email,
                first_name=str(row.get(field_map.get("first_name"), ""))[:100] if field_map.get("first_name") in row else None,
                last_name=str(row.get(field_map.get("last_name"), ""))[:100] if field_map.get("last_name") in row else None,
                full_name=str(row.get(field_map.get("full_name"), ""))[:255] if field_map.get("full_name") in row else None,
                company=str(row.get(field_map.get("company"), ""))[:255] if field_map.get("company") in row else None,
                website=str(row.get(field_map.get("website"), ""))[:500] if field_map.get("website") in row else None,
                country=str(row.get(field_map.get("country"), ""))[:100] if field_map.get("country") in row else None,
                phone=str(row.get(field_map.get("phone"), ""))[:50] if field_map.get("phone") in row else None,
                industry=str(row.get(field_map.get("industry"), ""))[:255] if field_map.get("industry") in row else None,
                job_title=str(row.get(field_map.get("job_title"), ""))[:255] if field_map.get("job_title") in row else None,
                source=source,
            )
            imported += 1

        return {
            "imported": imported,
            "duplicates": duplicates,
            "invalid": invalid,
            "total_processed": imported + duplicates + invalid,
        }
