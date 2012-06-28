PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE src(
	name text COLLATE NOCASE
);
CREATE TABLE modules(
	name text COLLATE NOCASE
);
CREATE TABLE binds(
	name text COLLATE NOCASE,
	module text COLLATE NOCASE,
	event text COLLATE NOCASE,
	command text COLLATE NOCASE
);
CREATE TABLE botnick(
	name text COLLATE NOCASE
);
COMMIT;
