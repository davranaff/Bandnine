# Writing Flow

Writing has the same exam lifecycle (create/start/submit), but a different submit model and scoring path.

## A) Catalog endpoints
- `GET /api/v1/writing/tests?offset=<int>&limit=<int>`
- `GET /api/v1/writing/tests/{test_id}`

What detail returns:
- `parts` and alias `writing_parts`.
- each part has prompt assets:
  - `task` text,
  - `image_url` (optional),
  - `file_urls` (optional list).
- answer spec is always text essay (`text_input` + `essay`).

## B) Exam attempt endpoints
- `POST /api/v1/exams/writing`
- `POST /api/v1/exams/writing/{exam_id}/start`
- `POST /api/v1/exams/writing/{exam_id}/submit`

## C) Submit payload format

```json
[
  { "part_id": 201, "essay": "Task 1 essay text..." },
  { "part_id": 202, "essay": "Task 2 essay text..." }
]
```

## D) Strict submit validation
Before save, backend checks:
- full set of writing parts is submitted;
- unknown `part_id` is rejected;
- duplicate `part_id` is rejected;
- `essay` is required after trim (non-empty).

On violation:
- returns `400` with `code=invalid_exam_submission`;
- no partial save.

## E) Save result behavior
On successful submit:
- each essay is saved per part (`WritingExamPart`);
- `is_checked` stays false until review;
- `score` can stay null initially;
- `corrections` initially indicates AI feedback is pending.

## F) AI evaluation path
After submit, backend enqueues ARQ jobs:
- job name: `evaluate_writing_exam_part`;
- one job per submitted writing part;
- up to 3 tries with exponential delay.

AI output is transformed into:
- estimated IELTS band,
- criteria breakdown,
- strengths,
- improvements,
- summary feedback text.

If AI fails after retries:
- `score = null`,
- `corrections` stores failure reason.

## G) Manual review path
Admin endpoint:
- `PATCH /api/v1/admin/exams/writing/parts/{exam_part_id}/review`

Manual review can set:
- `is_checked`,
- `score`,
- `corrections`.

If part is already manually checked, worker skips overwriting it.

## H) Timer and idempotency
- timer is in seconds and not capped;
- finish reason is `completed` or `time_is_up`;
- repeated submit after finish returns saved payload.
