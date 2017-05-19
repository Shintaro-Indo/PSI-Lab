drop table if exists teachers;
create table teachers(
  id integer primary key autoincrement,
  name text,
  research_theme text,
  introduction text,
  remarks1 text,
  graduation_thesis_theme text,
  aim text,
  contents_and_plan text,
  remarks2 text
);
