DROP TABLE IF EXISTS posts;

CREATE TABLE posts
(
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title   TEXT      NOT NULL,
    content TEXT      NOT NULL
);

DROP TABLE IF EXISTS metrics;

CREATE TABLE metrics
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT      NOT NULL,
    value           TEXT      NOT NULL,
    last_updated    TIMESTAMP NULL
);


