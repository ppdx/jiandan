CREATE TABLE IF NOT EXISTS `viewed-pages` (
	`page`	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(page)
);

CREATE TABLE IF NOT EXISTS `data` (
    `id`        INTEGER NOT NULL UNIQUE,
    `author`    TEXT NOT NULL,
    `content`   TEXT NOT NULL,
    PRIMARY KEY(id)
);