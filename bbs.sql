-- fraskrで使うデータベースを用意
-- 各エントリーを格納しておくテーブルで，titleとtextという属性を持つ．

drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title string not null,
  text string not null
);
