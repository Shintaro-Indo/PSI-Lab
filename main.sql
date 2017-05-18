drop table if exists system;
create table system (
  id integer primary key autoincrement,
  paragraph string not null --最後にコンマあるとエラー．
);
