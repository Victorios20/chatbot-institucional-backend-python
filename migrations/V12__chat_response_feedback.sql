-- Persist delivered answers and one editable evaluation per answer.
CREATE TABLE chatbot_responses (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id),
    request_id UUID NOT NULL,
    question TEXT NOT NULL CHECK (length(question) BETWEEN 1 AND 4000),
    answer TEXT NOT NULL,
    presentation JSONB,
    suggestions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (student_id, request_id)
);
CREATE INDEX chatbot_responses_student_created_idx ON chatbot_responses(student_id, created_at DESC);
CREATE TABLE chatbot_response_feedback (
    response_id UUID PRIMARY KEY REFERENCES chatbot_responses(id) ON DELETE CASCADE,
    rating VARCHAR(20) NOT NULL CHECK (rating IN ('helpful', 'not_helpful')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
