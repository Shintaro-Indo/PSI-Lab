drop table if exists system;
create table system (
  id integer primary key autoincrement,
  paragraph string not null --最後にコンマあるとエラー．
);

drop table if exists tmi;
create table tmi (
  id integer primary key autoincrement,
  paragraph string not null
);

drop table if exists aichi;
create table aichi(
  id integer primary key autoincrement,
  paragraph string not null,
);
