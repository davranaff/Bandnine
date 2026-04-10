from decimal import Decimal

from pydantic import BaseModel


class ReadingTestIn(BaseModel):
    title: str
    description: str
    time_limit: int
    is_active: bool = True


class ReadingPassageIn(BaseModel):
    title: str
    content: str
    passage_number: int


class ReadingBlockIn(BaseModel):
    title: str
    description: str
    block_type: str
    order: int
    question_heading: str | None = None
    list_of_headings: str | None = None
    table_completion: str | None = None
    flow_chart_completion: str | None = None


class ReadingQuestionIn(BaseModel):
    question_text: str
    order: int


class QuestionOptionIn(BaseModel):
    option_text: str
    is_correct: bool = False
    order: int = 0


class QuestionAnswerIn(BaseModel):
    correct_answers: str


class ListeningTestIn(BaseModel):
    title: str
    description: str
    time_limit: int
    is_active: bool = True
    voice_url: str | None = None


class ListeningPartIn(BaseModel):
    title: str
    order: int


class ListeningBlockIn(BaseModel):
    title: str
    description: str
    block_type: str
    order: int
    table_completion: str | None = None


class ListeningQuestionIn(BaseModel):
    question_text: str
    order: int


class WritingTestIn(BaseModel):
    title: str
    description: str
    time_limit: int
    is_active: bool = True


class WritingPartIn(BaseModel):
    order: int
    task: str
    image_url: str | None = None
    file_urls: list[str] | None = None


class WritingReviewIn(BaseModel):
    is_checked: bool = True
    corrections: str | None = None
    score: Decimal | None = None


class CategoryIn(BaseModel):
    title: str
    slug: str


class LessonIn(BaseModel):
    category_id: int
    title: str
    video_link: str
