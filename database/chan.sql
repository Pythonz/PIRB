PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE list(
	channel text COLLATE NOCASE
);
CREATE TABLE channel(
	channel text COLLATE NOCASE,
	auth text COLLATE NOCASE,
	flags text COLLATE NOCASE
);
CREATE TABLE info(
	channel text COLLATE NOCASE,
	topic text COLLATE NOCASE,
	modes text COLLATE NOCASE
);
CREATE TABLE bans(
	channel text COLLATE NOCASE,
	ban text COLLATE NOCASE
);
CREATE TABLE exempts(
	channel text COLLATE NOCASE,
	exempt text COLLATE NOCASE
);
COMMIT;
