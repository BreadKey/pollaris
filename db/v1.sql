create database pollaris;

use pollaris;

create table Users(
    id varchar(20),
    password varchar(100) not null,
    nickname varchar(10),
    hasIdentity tinyint(1),
    primary key(id),
    unique key(nickname)
);

create table Roles(
    userId varchar(20),
    name varchar(20),
    primary key(userId, name),
    foreign key(userId) references Users(id) on delete cascade
);

create table VerificationCodes(
    id bigint auto_increment primary key,
    userId varchar(20) not null,
    phoneNumber varchar(100) unique key not null,
    code varchar(100) not null,
    requestDateTime datetime not null,
    foreign key(userId) references Users(id) on delete cascade
);

create table VerificationLogs(
    id bigint auto_increment primary key,
    userId varchar(20) not null,
    phoneNumber varchar(100) unique key not null,
    dateTime datetime not null,
    foreign key(userId) references Users(id) on delete cascade
);

create table Identities(
    userId varchar(20),
    method varchar(10),
    value varchar(100),
    primary key(userId, method),
    foreign key(userId) references Users(id) on delete cascade
);

create table Polls(
    id bigint auto_increment,
    userId varchar(20),
    question varchar(100),
    primary key(id),
    foreign key(userId) references Users(id)
);

create table Options(
    pollId bigint,
    `index` int,
    body varchar(30),
    count bigint,
    primary key(pollId, `index`),
    foreign key(pollId) references Polls(id) on delete cascade
);

create table Answers(
    userId varchar(20),
    pollId bigint,
    `index` int,
    primary key(userId, pollId),
    foreign key (pollId) references Polls(id) on delete cascade
);