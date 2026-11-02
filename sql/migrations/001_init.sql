-- 001: initial schema (matches src/assistant_api/db.py)
CREATE TABLE IF NOT EXISTS chat_session (
    id          VARCHAR(16) PRIMARY KEY,           -- salted hash of the session id
    channel     VARCHAR(16) NOT NULL DEFAULT 'web',
    created_at  TIMESTAMP   NOT NULL
);
CREATE TABLE IF NOT EXISTS interaction (
    id          INTEGER PRIMARY KEY,
    request_id  VARCHAR(32) NOT NULL UNIQUE,
    session_id  VARCHAR(16) NOT NULL REFERENCES chat_session(id),
    intent      VARCHAR(16) NOT NULL,
    topic       VARCHAR(32),
    resolved    BOOLEAN     NOT NULL DEFAULT 1,
    degraded    BOOLEAN     NOT NULL DEFAULT 0,
    latency_ms  FLOAT       NOT NULL DEFAULT 0,
    created_at  TIMESTAMP   NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_interaction_intent     ON interaction(intent);
CREATE INDEX IF NOT EXISTS ix_interaction_session_id ON interaction(session_id);
CREATE INDEX IF NOT EXISTS ix_interaction_created_at ON interaction(created_at);
CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER PRIMARY KEY,
    request_id  VARCHAR(32) NOT NULL REFERENCES interaction(request_id),
    rating      INTEGER     NOT NULL CHECK (rating IN (-1, 0, 1)),
    comment     VARCHAR(500),
    created_at  TIMESTAMP   NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_feedback_request_id ON feedback(request_id);
