drop table if exists users;
    create table users (
    id integer primary key autoincrement,
    username text not null,
    password text not null,
    permissions text not null
);

DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    createdBy TEXT NOT NULL,
    FOREIGN KEY(createdBy) REFERENCES users(username)
);

DROP TABLE IF EXISTS pullRequests;
CREATE TABLE pullRequests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    createdBy TEXT NOT NULL,
    FOREIGN KEY(createdBy) REFERENCES users(username) 
);

DROP TABLE IF EXISTS jiras;
CREATE TABLE jiras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    createdBy TEXT NOT NULL,
    title TEXT NOT NULL, 
    type TEXT NOT NULL, 
    pullRequestID INTEGER,
    descriptions TEXT,
    approved INTEGER DEFAULT 0,
    FOREIGN KEY(pullRequestID) REFERENCES pullRequests(id),
    FOREIGN KEY(createdBy) REFERENCES users(username)
);

