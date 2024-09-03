
### IMPORTS 

# External imports
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from supabase import create_client, Client
from openai import OpenAI
from os import environ

# Python imports
import random
import time
import hmac
from datetime import datetime

# Internal imports

from llm import process_text_openai, stream_text_openai
from styling_css import page_config, page_styling
import config as c
import prompts as p


### INITIAL VARIABLES

# Initialize Supabase client
if c.run_mode == "local":
    SUPABASE_URL = st.secrets.supabase_db_url
    SUPABASE_KEY = st.secrets.supabase_db_api
else:
    SUPABASE_URL =  environ.get("supabase_db_url")
    SUPABASE_KEY =  environ.get("supabase_db_api")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


### STYLING - PAGE CONFIG
page_config()
page_styling()


### SESSION STATES

if "dashboard_id" not in st.session_state:
    st.session_state["dashboard_id"] = 1234
    dashboard_id = st.session_state["dashboard_id"]

selected_dashboard = supabase.table('admin_dashboard').select('*').eq('dashboard_id', int(st.session_state["dashboard_id"])).execute().data[0]

st.session_state.summarize_user_input = selected_dashboard.get('summarize_user_input', '')
#st.session_state.questions_to_users = selected_dashboard.get('questions_to_users', '')
#st.session_state.risks_to_users = selected_dashboard.get('risks_to_users', '')
#st.session_state.ideas_to_users = selected_dashboard.get('ideas_to_users', '')


### MAIN APP ###########################

def main():

    ###################################
    ### SIDEBAR

    # MENU

    st.sidebar.markdown("## FeedbackFabriken")

    st.sidebar.page_link("app.py", label="Feedback", icon=":material/home:")
    st.sidebar.page_link("pages/10Dashboard.py", label="Dashboard", icon=":material/dashboard:")

    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")
    st.sidebar.markdown("### :material/settings: Inställningar")

    # Reset session state on page load
    #if "dashboard_id" not in st.session_state:
    #    st.session_state["dashboard_id"] = "1234"

    # Fetch dashboards
    #dashboards = supabase.table('admin_dashboard').select('dashboard_id').execute()

    # Live mode switch
    live_mode = st.sidebar.checkbox('Live mode')

    st.sidebar.markdown(
        "#"
        )
    
    st.sidebar.markdown(f"""
            __Version:__ {c.app_version}  
            __Senast uppdaterad:__ {c.app_updated_date}       
                        """)
    

    ####################################
    ### MAIN PAGE

    st.title(":material/dashboard: Dashboard")

    col1, col2, col3 = st.columns([6, 6, 6], gap = "medium", vertical_alignment = "top")
    
    # COL 1

    with col1:

        col1_subcol1, col1_subcol2 = st.columns([2, 2], gap = "medium", vertical_alignment = "top")

        ### Container Workshop 
        
        with col1_subcol1:

            container_dashboard_id = stylable_container(key = "column-1", css_styles = """
                    {
                    border: 0px solid rgba(255, 255, 255, 0.2);
                    background: rgb(17,77,110);
                    background: linear-gradient(90deg, rgb(240 240 240) 0%, rgb(245 243 243) 100%);
                    border-radius: 8px;
                    padding: 1rem 1rem 1rem 1rem;                                       
                    }
                    """)
            container_dashboard_id.caption("Dashboard ID")

            if 'dashboard_id' in st.session_state:
                container_dashboard_id.markdown(f"# {st.session_state.dashboard_id}")


        with col1_subcol2:

            # Container Number of user entries
            container_user_entries = stylable_container(key = "column-2", css_styles = """
                    {
                    border: 0px solid rgba(255, 255, 255, 0.2);
                    background: rgb(17,77,110);
                    background: linear-gradient(90deg, rgb(240 240 240) 0%, rgb(245 243 243) 100%);
                    border-radius: 8px;
                    padding: 1rem 1rem 1rem 1rem;                                       
                    }
                                                            """)
            container_user_entries.caption("Antal svarande")
            entry_container = container_user_entries.empty()


        # Container questions to users
        #container_questions_to_users = stylable_container(key = "questions_to_users", css_styles = """
        #        {
        #        border: 0px solid rgba(255, 255, 255, 0.2);
        #        background: rgb(17,77,110);
        #        background: linear-gradient(90deg, rgba(17,77,110,1) 0%, rgba(26,117,167,1) 100%);
        #        border-radius: 8px;
        #        padding: 1rem 1rem 1rem 1rem;                                       
        #        }
        #                                                """)
        #container_questions_to_users.markdown("###### Frågor att jobba med")
        #questions_to_users_container = container_questions_to_users.empty()

        #if 'questions_to_users' in st.session_state:
        #    questions_to_users_container.markdown(st.session_state.questions_to_users)


        # Container risks to users
        #container_risks_to_users = stylable_container(key = "risks_to_users", css_styles = """
        #        {
        #        border: 0px solid rgba(255, 255, 255, 0.2);
        #        background: rgb(17,77,110);
        #        background: linear-gradient(90deg, rgba(17,77,110,1) 0%, rgba(26,117,167,1) 100%);
        #        border-radius: 8px;
        #        padding: 1rem 1rem 1rem 1rem;                                       
        #        }
        #                                                """)
        #container_risks_to_users.markdown("###### Risker att jobba med")
        #risks_to_users_container = container_risks_to_users.empty()

        #if 'risks_to_users' in st.session_state:
        #    risks_to_users_container.markdown(st.session_state.risks_to_users)


        # Container ideas to users
        #container_ideas_to_users = stylable_container(key = "ideas_to_users", css_styles = """
        #        {
        #        border: 0px solid rgba(255, 255, 255, 0.2);
        #        background: rgb(17,77,110);
        #        background: linear-gradient(90deg, rgba(17,77,110,1) 0%, rgba(26,117,167,1) 100%);
        #        border-radius: 8px;
        #        padding: 1rem 1rem 1rem 1rem;                                       
        #        }
        #                                                """)
        #container_ideas_to_users.markdown("###### Idéer från LEA att jobba med")
        #ideas_to_users_container = container_ideas_to_users.empty()

        #if 'ideas_to_users' in st.session_state:
        #    ideas_to_users_container.markdown(st.session_state.ideas_to_users)


    
    # COL 2
    
    with col2:
        
        container_summarize = stylable_container(key = "summarize", css_styles = """
                {
                border: 0px solid rgba(255, 255, 255, 0.2);
                padding: 0rem 0rem 0rem 0rem;                                       
                }
                """)

        summarized_imput = container_summarize.empty()
        summarized_imput.caption("Summering")

        if 'summarize_user_input' in st.session_state:
            summarized_imput.markdown(st.session_state.summarize_user_input)
            

    
    # COL 3
    
    with col3:
        
        with stylable_container(key = "column-3", css_styles = """
                {
                border: 0px solid rgba(255, 255, 255, 0.2);
                background: linear-gradient(90deg, rgb(240 240 240) 0%, rgb(245 243 243) 100%);
                border-radius: 8px;
                padding: 1rem 1rem 1rem 1rem;                                       
                }"""):
            
            st.caption("Inkommen feedback")
            feedback = st.empty()
    

            def collect_user_input():
                dashboard_id = st.session_state.dashboard_id
                
                if dashboard_id:
                    # Fetch all records for the current workshop
                    records = supabase.table('feedback').select('processed_text').eq('dashboard_id', int(dashboard_id)).execute()
                    if records.data:
                        # Collect all content from processed_text with separator
                        collected_user_input = "\n--- New user ---\n".join(record['processed_text'] for record in records.data if record['processed_text'])
                        return collected_user_input
                return ""
            

            def fetch_records():
                
                dashboard_id = st.session_state.dashboard_id
                
                if dashboard_id:
                    # Fetch the records for the given dashboard_id
                    records = supabase.table('feedback').select('id', 'processed_text', 'collected', 'created_at').eq('dashboard_id', int(dashboard_id)).order('id', desc=False).execute()
                    record_ids = [record['id'] for record in records.data]

                    # Fetch the current workshop_admin entry for the dashboard_id
                    admin_records = supabase.table('admin_dashboard').select('participant_entries_ids').eq('dashboard_id', int(dashboard_id)).execute().data
                    
                    if not admin_records:
                        # If no admin record exists for this dashboard_id, return the records without updating participant_entries_ids
                        return records.data

                    admin_record = admin_records[0]

                    # Get the current list of participant_entries_ids and ensure they are integers
                    participant_entries_ids = [int(id) for id in admin_record['participant_entries_ids']]

                    # Check if there are new entries
                    new_entries = set(record_ids) - set(participant_entries_ids)

                    if new_entries:
                        # Update the workshop_admin entry with the new list of IDs
                        updated_participant_entries_ids = list(set(participant_entries_ids + record_ids))
                        supabase.table('admin_dashboard').update({'participant_entries_ids': updated_participant_entries_ids}).eq('dashboard_id', int(dashboard_id)).execute()

                    return records.data
                return []

            
            if live_mode:
                
                while True:
                    records = fetch_records()
                    count_number_of_entries = 0
                
                    if records:
                        with feedback.container():
                            for record in reversed(records):
                                if not record.get('collected'):
                                    st.toast('Hooray! Nytt bidrag!', icon='🎉')

                                    # Update the record in the database
                                    supabase.table('feedback').update({'collected': "Done"}).eq('id', record['id']).execute()
                                    record['collected'] = "Done"  # Update the local record
                                    
                                    # Process and summarize user input
                                    user_input = collect_user_input()
                                    summarize_user_input = stream_text_openai(p.prompt_summarize, user_input, summarized_imput)
                                    #questions_to_users = stream_text_openai(system_prompt_questions_to_users, user_input, questions_to_users_container)
                                    #risks_to_users = stream_text_openai(system_prompt_risks_to_users, user_input, risks_to_users_container)
                                    #ideas_to_users = stream_text_openai(system_prompt_ideas_to_users, user_input, ideas_to_users_container)
                                    
                                    # Update the workshop_admin table with the latest values
                                    supabase.table('admin_dashboard').update({
                                        'summarize_user_input': summarize_user_input
                                        #'questions_to_users': questions_to_users,
                                        #'risks_to_users': risks_to_users,
                                        #'ideas_to_users': ideas_to_users
                                    }).eq('dashboard_id', st.session_state.dashboard_id).execute()

                                    count_number_of_entries += 1
                                
                                entry_id = record['id']
                                created_at = datetime.fromisoformat(record['created_at'])
                                formatted_time = created_at.strftime('%H:%M')
                                
                                with st.expander(f"{entry_id} - Mottaget {formatted_time}"):
                                    st.write(f"{record['processed_text']}")
                                    count_number_of_entries += 1
                    
                    entry_container.markdown(f"# {count_number_of_entries}")
                    time.sleep(c.loop_time)


            else:
                records = fetch_records()
                count_number_of_entries = 0

                if records:
                    with feedback.container():
                        for record in reversed(records):

                            entry_id = record['id']
                            created_at = datetime.fromisoformat(record['created_at'])
                            formatted_time = created_at.strftime('%H:%M')
                            count_number_of_entries += 1

                            with st.expander(f"{entry_id} - Mottaget {formatted_time}"):
                                st.write(f"{record['processed_text']}")
                                
                else:
                    st.write('Inget inskickat ännu')
                
                entry_container.markdown(f"# {count_number_of_entries}")



if __name__ == "__main__":
    main()
