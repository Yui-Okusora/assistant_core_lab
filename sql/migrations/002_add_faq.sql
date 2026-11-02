-- 002: FAQ records curated by staff (schema evolution example)
CREATE TABLE IF NOT EXISTS faq (
    id          INTEGER PRIMARY KEY,
    question    VARCHAR(300) NOT NULL,
    answer      TEXT         NOT NULL,
    source_id   VARCHAR(32),                       -- handbook rule id (provenance)
    updated_at  TIMESTAMP    NOT NULL,
    updated_by  VARCHAR(32)  NOT NULL               -- staff role, not a personal name
);
