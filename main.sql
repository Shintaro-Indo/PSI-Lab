drop table if exists teachers;
create table teachers(
  id integer primary key autoincrement,
  name text,
  affiliation text, --所属
  specialized_field text, --専門分野
  research_theme text, --研究テーマ
  number_of_people text, --標準受け入れ人数
  place text, --実施場所
  keywords text
);
