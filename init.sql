create database if not exists pollaris;

use pollaris;

create table Polls(
    id bigint auto_increment,
    userId varchar(20),
    question varchar(100),
    primary key(id)
);

create table Options(
    pollId bigint,
    `index` int,
    body varchar(100),
    count bigint,
    primary key(pollId, `index`),
    foreign key (pollId) references Polls(id) on delete cascade
);

create table Answers(
    userId varchar(20),
    pollId bigint,
    `index` int,
    primary key(userId, pollId),
    foreign key (pollId) references Polls(id) on delete cascade
);