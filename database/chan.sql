PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE list(channel text);
CREATE TABLE channel(channel text, auth text, flags text);
CREATE TABLE info(channel text, topic text, modes text);
CREATE TABLE bans(channel text, ban text);
CREATE TABLE exempts(channel text, exempt text);
COMMIT;
