from app.models.domain import Domain, DNSRecord, DomainHealth
from app.repositories.base import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    def __init__(self, db):
        super().__init__(db, Domain)


class DNSRecordRepository(BaseRepository[DNSRecord]):
    def __init__(self, db):
        super().__init__(db, DNSRecord)


class DomainHealthRepository(BaseRepository[DomainHealth]):
    def __init__(self, db):
        super().__init__(db, DomainHealth)
