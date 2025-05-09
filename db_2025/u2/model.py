from uuid import UUID

from pydantic import BaseModel


class Student(BaseModel):
    student_id: int
    album: str
    name: str


class Upload(BaseModel):
    file_id: UUID
    filename: str
    owner: int


# + table Upload_Students where many students as co-authors can be attached to single Upload
