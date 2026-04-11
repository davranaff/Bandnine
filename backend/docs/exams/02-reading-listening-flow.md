# Reading and Listening Flow

This document covers both catalog usage and exam submit behavior for `reading` and `listening`.

## A) Catalog endpoints (before exam attempt)
Reading:
- `GET /api/v1/reading/tests?offset=<int>&limit=<int>`
- `GET /api/v1/reading/tests/{test_id}`

Listening:
- `GET /api/v1/listening/tests?offset=<int>&limit=<int>`
- `GET /api/v1/listening/tests/{test_id}`

Catalog pagination:
- Uses `offset + limit`.
- Response shape: `{ "items": [...], "limit": N, "offset": M }`.

## B) Detail payload structure
Reading detail includes:
- `parts` and alias `passages` (same data).
- part -> block -> questions hierarchy.
- per question: `id`, `number`, `question_text`, `options`.
- per block: `block_type` + `answer_spec` + optional `table_json`.

Listening detail includes:
- one shared `voice_url` for the whole test.
- alias `audio_url` (same value as `voice_url`).
- `parts` hierarchy with blocks/questions.
- same answer spec idea as reading (`single_choice` or `text_input`).

## C) Exam attempt endpoints
Reading:
- `POST /api/v1/exams/reading`
- `POST /api/v1/exams/reading/{exam_id}/start`
- `POST /api/v1/exams/reading/{exam_id}/submit`

Listening:
- `POST /api/v1/exams/listening`
- `POST /api/v1/exams/listening/{exam_id}/start`
- `POST /api/v1/exams/listening/{exam_id}/submit`

## D) Submit payload format
`reading` and `listening` use the same body:

```json
[
  { "id": 101, "value": "B" },
  { "id": 102, "value": "Not Given" }
]
```

Where:
- `id`: question id.
- `value`: user answer as string.

## E) Submit validation (strict)
Before save, backend validates all answers:
- full set of answers is required;
- unknown question ids are rejected;
- duplicate question ids are rejected;
- for single-choice blocks, `value` must match one of question options;
- for text-input blocks, `value` is trimmed string;
- if block has `max_words`, limit is enforced.

On any violation:
- returns `400` with `code=invalid_exam_submission`;
- nothing is saved (fail whole submit).

## F) Scoring and correctness
After valid submit:
- backend stores `user_answer`, `correct_answer`, `is_correct` for each question;
- answer matching is trim + case-insensitive;
- reading/listening score uses current IELTS raw-to-band scale (`reading_band_score`);
- `correct_answers` is returned as count of correct responses.

## G) Timer and finish reason
- timer is measured in seconds;
- `time_spent = finished_at - started_at`;
- `time_spent` is not capped;
- `finish_reason = time_is_up` when elapsed >= `time_limit`, else `completed`.

## H) Idempotency
- repeated `start` keeps original `started_at`;
- repeated `submit` after finish returns saved result, no rewrite.
