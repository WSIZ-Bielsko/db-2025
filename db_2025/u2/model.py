from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FileMeta(BaseModel):
    id: UUID
    original_file_name: str
    owner_id: int
    owner_name_short: str
    size_mb: int
    upload_date: datetime
    is_public: bool
    is_frozen: bool


class Category(BaseModel):
    id: UUID
    name: str
    przedmiot_id: int | None
    is_public: bool
    comment: str


"""

 Notes for FileMeta:
    - is_public: accessible by all, else accessible by authors & teachers
    - is_frozen: removal only possible for 5 minutes after upload
    - owner name short: given name + 3 letters of surname

 Notes for Category:
    - is_public: visible to all users; else - only if student has given przedmiot_id (last 2sems)
"""


# relations
class FileCategory:
    file_id: UUID
    cat_id: UUID


class FileAuthor:
    file_id: UUID
    author_id: int
