from app.models.validation import ValidationResult
from app.repositories.base import BaseRepository


class ValidationResultRepository(BaseRepository[ValidationResult]):
    def __init__(self, db):
        super().__init__(db, ValidationResult)
