# FeedbackFabriken

### Vad?
Text text

### Kort teknisk beskrivning
En Python Streamlit-applikation med en sida för att ge feedback och en sida med en dashboard där statistik genereras utifrån feedback.  
AI-tjänster som används är Whisper och GPT-4o från OpenAI för transkribering samt bearbetning och generering av text.  
Data sparas i en databas från Supabase.

### Supabase databas

```
## Admin Dashboard Table

create table admin_dashboard (
  id serial primary key,
  created_at timestamp not null default current_timestamp,
  dashboard_id int not null,
  participant_entries_ids text[] default array[]::text[],
  summarize_user_input text,
  summarize_leadership text,
  summarize_work_environment text,
  summarize_equality text,
  summarize_misc text,
  image_url text,
  summarize_ideas text,
  summarize_leadership_recommendation text,
  summarize_work_environment_recommendation text,
  summarize_equality_recommendation text,
  summarize_misc_recommendation text
);



## Feedback table

create table feedback (
  id serial primary key,
  created_at timestamp not null default current_timestamp,
  dashboard_id int not null,
  processed_text text,
  collected text
);
```

### Juridisk information
Den här applikationen är inte GDPR-säkrad. Den är en del av ett utforskande och ska ses som en POC - proof of concept.
