from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    title: str
    slug: str


class LessonOut(BaseModel):
    id: int
    category_id: int
    title: str
    video_link: str


class CategoryIn(BaseModel):
    title: str
    slug: str


class LessonIn(BaseModel):
    category_id: int
    title: str
    video_link: str
