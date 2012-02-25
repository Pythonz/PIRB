PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE src(name text);
CREATE TABLE modules(name text);
CREATE TABLE binds(name text, module text, event text, command text);
CREATE TABLE botnick(name text);
CREATE TABLE put_query(id integer primary key autoincrement, message text);
COMMIT;
