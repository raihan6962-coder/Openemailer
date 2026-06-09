from app.models.template import Template, TemplateVersion
from app.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    def __init__(self, db):
        super().__init__(db, Template)


class TemplateVersionRepository(BaseRepository[TemplateVersion]):
    def __init__(self, db):
        super().__init__(db, TemplateVersion)
