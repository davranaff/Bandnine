from dataclasses import dataclass, field

from app.modules.listening.service import question_numbering as listening_question_numbering
from app.modules.reading.service import question_numbering as reading_question_numbering


@dataclass
class FakeQuestion:
    id: int
    order: int


@dataclass
class FakeBlock:
    order: int
    questions: list[FakeQuestion] = field(default_factory=list)


@dataclass
class FakePassage:
    passage_number: int
    question_blocks: list[FakeBlock] = field(default_factory=list)


@dataclass
class FakePart:
    order: int
    question_blocks: list[FakeBlock] = field(default_factory=list)


@dataclass
class FakeReadingTest:
    passages: list[FakePassage]


@dataclass
class FakeListeningTest:
    parts: list[FakePart]


def test_reading_question_global_numbering() -> None:
    test = FakeReadingTest(
        passages=[
            FakePassage(
                passage_number=1,
                question_blocks=[
                    FakeBlock(order=1, questions=[FakeQuestion(id=10, order=1), FakeQuestion(id=11, order=2)]),
                ],
            ),
            FakePassage(
                passage_number=2,
                question_blocks=[
                    FakeBlock(order=1, questions=[FakeQuestion(id=20, order=1)]),
                ],
            ),
        ]
    )

    numbering = reading_question_numbering(test)  # type: ignore[arg-type]
    assert numbering == {10: 1, 11: 2, 20: 3}


def test_listening_question_global_numbering() -> None:
    test = FakeListeningTest(
        parts=[
            FakePart(order=1, question_blocks=[FakeBlock(order=1, questions=[FakeQuestion(id=100, order=1)])]),
            FakePart(order=2, question_blocks=[FakeBlock(order=1, questions=[FakeQuestion(id=101, order=1)])]),
        ]
    )

    numbering = listening_question_numbering(test)  # type: ignore[arg-type]
    assert numbering == {100: 1, 101: 2}
