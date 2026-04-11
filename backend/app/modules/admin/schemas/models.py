from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AdminBaseModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ReadingTestIn(AdminBaseModel):
    title: str
    description: str
    time_limit: int
    is_active: bool = True


class ReadingPassageIn(AdminBaseModel):
    title: str
    content: str
    passage_number: int


class ReadingBlockIn(AdminBaseModel):
    title: str
    description: str
    block_type: str
    order: int
    question_heading: str | None = None
    list_of_headings: str | None = None
    table_completion: str | None = None
    flow_chart_completion: str | None = None


class ReadingQuestionIn(AdminBaseModel):
    question_text: str
    order: int


class QuestionOptionIn(AdminBaseModel):
    option_text: str
    is_correct: bool = False
    order: int = 0


class QuestionAnswerIn(AdminBaseModel):
    correct_answers: str


class ListeningTestIn(AdminBaseModel):
    title: str
    description: str
    time_limit: int
    is_active: bool = True
    voice_url: str | None = None


class ListeningPartIn(AdminBaseModel):
    title: str
    order: int


class ListeningBlockIn(AdminBaseModel):
    title: str
    description: str
    block_type: str
    order: int
    table_completion: str | None = None


class ListeningQuestionIn(AdminBaseModel):
    question_text: str
    order: int


class WritingTestIn(AdminBaseModel):
    title: str
    description: str
    time_limit: int
    is_active: bool = True


class WritingPartIn(AdminBaseModel):
    order: int
    task: str
    image_url: str | None = None
    file_urls: list[str] | None = None


class WritingReviewIn(AdminBaseModel):
    is_checked: bool = True
    corrections: str | None = None
    score: Decimal | None = None


class CategoryIn(AdminBaseModel):
    title: str
    slug: str


class LessonIn(AdminBaseModel):
    category_id: int
    title: str
    video_link: str
