# Clara

Clara är av flera prototyper som togs fram inom projektet "Top of Mind: Jämställdhet i industrins vardag".
Projektets sida hittar du på https://www.ri.se/sv/vad-vi-gor/projekt/top-of-mind-jamstalldhet-i-industrins-vardag

## Bakgrund
**Att våga göra sin röst hörd och säga det man tycker, eller att säga ifrån, är svårt. Det kan handla om allt från att någon beter 
sig illa, till att man upplever orättvisor och ojämställdhet på sin arbetsplats. Men det kan också handla om idéer och förslag som skulle 
kunna göra arbetsplatsen bättre.**  

Clara är en prototyp som möjliggör att anonymt kunna göra sin röst hörd. Medarbetaren kan prata eller skriva in det du vill säga och AI anonymiserar det.
Medarbetaren har dessutom tillgång till en chatbot att rådfråga.  
Därefter analyseras och sammanställs alla medarbetares tankar i en dashboard, som exempelvis chefer och/eller HR skulle kunna ha tillgång till. Clara delar upp 
medarbetarnas röster i kategorierna 'Ledarskap', 'Arbetsmiljö', 'Jämställdhet', 'Övrigt' och 'Idéer'. AI hjälper dessutom till att ta fram rekommendationer 
kring kategorierna.  

## Hur funkar det?



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
