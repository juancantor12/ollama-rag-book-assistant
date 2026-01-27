# Quiz and Test Generation Roadmap (API)

Goal
- Extend the backend so the assistant can generate quizzes/tests from books, not only answer questions. Support three question types: multiple choice (single answer), open text with follow-ups, and coding questions with deterministic execution and expected output.

Scope summary
- Add a topic index per book (chapter -> topics). The UI can request quiz generation for a chapter or topic.
- Add quiz/session APIs with stateful evaluation and hinting.
- Add safe code evaluation flow for coding questions (start with Python-only unless expanded).

Phase 1 - Topic index per book
1) New indexing module
- Add `src/app/indexer.py` to build a chapter/topic index from each book.
- Use existing TOC + page parsing from `src/app/generate_embeddings.py` to compute chapter page ranges.
- For each chapter, call the chat model once with the chapter text window(s) and generate a structured JSON summary:
  - `chapter_id`, `title`, `page_start`, `page_end`
  - `topics`: list of `{name, description, keywords, page_refs}`
- Store as `output/<BookName>/topics_index.json`.
- Add `src/app/index_store.py` with read/write helpers and schema validation.

2) API routes for index
- Add `GET /books/{book_filename}/topics/` to return `topics_index.json`.
- Add `POST /books/{book_filename}/topics/refresh/` to regenerate the index (reusing the embeddings parsing path).
- Add `GET /books/{book_filename}/chapters/` to return chapter metadata only.

3) Permissions
- Add RBAC permissions: `view_topics`, `refresh_topics`.
- Update permissions seed logic (if any) or document manual creation via admin UI.

Phase 2 - Quiz data model (API DB)
1) SQLAlchemy models (new files in `src/api/models/`)
- `QuizSession`:
  - `id`, `user_id`, `book_filename`, `topic`, `chapter_id`, `question_count`, `type_distribution`, `status`, `created_at`, `updated_at`
- `QuizQuestion`:
  - `id`, `quiz_id`, `position`, `type`, `prompt`, `options` (JSON), `correct_answer`, `rubric`, `hints` (JSON), `test_spec` (JSON)
- `QuizAnswer`:
  - `id`, `quiz_id`, `question_id`, `attempt`, `answer_text`, `is_correct`, `feedback`, `created_at`
- Keep JSON fields as TEXT with JSON encoding for SQLite consistency.

2) Pydantic schemas (new files in `src/api/schemas/`)
- `QuizGenerateRequest`, `QuizSessionResponse`, `QuizQuestionResponse`, `AnswerSubmitRequest`, `AnswerSubmitResponse`, `QuizSummaryResponse`.

3) Controller
- Add `src/api/controllers/quiz.py` for creation, evaluation, and progression logic.

Phase 3 - Quiz generation + evaluation flow
1) Quiz generation
- Add `app/quiz_generator.py` to build questions using the index and chunked book context (reuse embeddings).
- Use strict JSON output from the LLM with these fields per question:
  - `type`, `prompt`, `options` (if MC), `correct_answer`, `rubric`, `hint_steps`, `test_spec` (if coding)
- Validate and sanitize before saving to DB.

2) Evaluation rules
- Multiple choice: exact match on `correct_answer`.
- Open text:
  - Use LLM grader with a rubric and minimum criteria.
  - If not correct, return a follow-up question (stored in `QuizAnswer.feedback`).
- Coding:
  - Execute user code with a predefined `test_spec` (function name, args, expected output).
  - Start with Python-only via a restricted runner (timeout + no file/network access).
  - Return pass/fail and provide incremental hints.

3) Code runner
- Add `src/app/code_runner.py` to run user-submitted code safely:
  - Restrict builtins, disable imports, enforce timeouts.
  - Standardize result format: `{stdout, stderr, passed, failure_reason}`.

Phase 4 - API endpoints
1) New routes in `src/api/routes/client.py` or a new `src/api/routes/quiz.py`
- `GET /books/{book_filename}/topics/`
- `POST /books/{book_filename}/topics/refresh/`
- `GET /books/{book_filename}/chapters/`
- `POST /quiz/generate/`
- `GET /quiz/{quiz_id}/`
- `POST /quiz/{quiz_id}/answer/`
- `POST /quiz/{quiz_id}/hint/`
- `GET /quiz/{quiz_id}/summary/`

2) Request/response details
- `POST /quiz/generate/` body:
  - `book_filename`, `chapter_id` or `topic`, `total_questions`, `type_distribution` (mc/open/coding)
- `POST /quiz/{quiz_id}/answer/` body:
  - `question_id`, `answer_text`, optional `code` for coding type.
- Responses return current question, evaluation feedback, and next action.

Phase 5 - RBAC + permissions
- Add permissions: `generate_quiz`, `take_quiz`, `submit_answer`, `run_code`.
- Update permission checks in new routes using `require_permission`.

Phase 6 - Tests
- Unit tests for indexer and quiz generator output shape.
- Integration tests for quiz session progression and evaluation outcomes.

Notes and guardrails
- Keep index and quiz generation deterministic by using temperature=0 or near-zero.
- Validate JSON from LLM before saving.
- Log all quiz sessions and answers under `output/<BookName>/` as optional JSON for debugging.
