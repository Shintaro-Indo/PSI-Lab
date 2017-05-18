drop table if exists test;
create table test ( --testはtable名．
  id integer primary key autoincrement,
  username string not null,
  message string not null
);
