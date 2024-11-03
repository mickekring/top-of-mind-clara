
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
from datetime import datetime, date

# Internal imports

from functions.llm import process_text_openai_recommendation, stream_text_openai, process_text_openai_image_prompt
from functions.image import download_image, create_image
from functions.styling_css import page_config, page_styling
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
    st.session_state["dashboard_id"] = c.dashboard_id
    dashboard_id = st.session_state["dashboard_id"]

selected_dashboard = supabase.table('admin_dashboard').select('*').eq('dashboard_id', int(st.session_state["dashboard_id"])).execute().data[0]

st.session_state.summarize_user_input = selected_dashboard.get('summarize_user_input', '')
st.session_state.summarize_leadership = selected_dashboard.get('summarize_leadership', '')
st.session_state.summarize_leadership_recommendation = selected_dashboard.get('summarize_leadership_recommendation', '')
st.session_state.summarize_work_environment = selected_dashboard.get('summarize_work_environment', '')
st.session_state.summarize_work_environment_recommendation = selected_dashboard.get('summarize_work_environment_recommendation', '')
st.session_state.summarize_equality = selected_dashboard.get('summarize_equality', '')
st.session_state.summarize_equality_recommendation = selected_dashboard.get('summarize_equality_recommendation', '')
st.session_state.summarize_misc = selected_dashboard.get('summarize_misc', '')
st.session_state.summarize_misc_recommendation = selected_dashboard.get('summarize_misc_recommendation', '')
st.session_state.summarize_ideas = selected_dashboard.get('summarize_ideas', '')
st.session_state.image_url = selected_dashboard.get('image_url', '')


### MAIN APP ###########################

def main():

    ###################################
    ### SIDEBAR

    # MENU

    st.sidebar.markdown(f"# {c.app_name}")

    st.sidebar.page_link("app.py", label="Feedback", icon=":material/home:")
    st.sidebar.page_link("pages/10Dashboard.py", label="Dashboard", icon=":material/dashboard:")

    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")

    # Reset session state on page load
    if "dashboard_id" not in st.session_state:
        st.session_state["dashboard_id"] = c.dashboard_id

    # Fetch dashboards
    #dashboards = supabase.table('admin_dashboard').select('dashboard_id').execute()

    # Live mode switch
    st.sidebar.markdown("### :material/play_circle: Live mode")
    st.sidebar.write("Om du vill ha realtidsuppdateringar aktiverar du live mode")
    live_mode = st.sidebar.checkbox('Live mode')
    st.sidebar.divider()


    def delete_feedback_and_reset_dashboard():
        # Delete all rows in the 'feedback' table
        supabase.table('feedback').delete().neq('id', 0).execute()  # Deletes all rows by selecting non-zero ids (workaround since supabase might not support blanket delete)

        # Reset the 'participant_entries_ids' field in the 'admin_dashboard' table
        supabase.table('admin_dashboard').update({'participant_entries_ids': []}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_user_input': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_leadership': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_work_environment': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_equality': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_misc': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_ideas': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_leadership_recommendation': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_work_environment_recommendation': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_equality_recommendation': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'summarize_misc_recommendation': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()
        supabase.table('admin_dashboard').update({'image_url': ""}).eq('dashboard_id', st.session_state.dashboard_id).execute()


        st.success('All feedback entries deleted and participant_entries_ids reset.')

    # Add a button for deletion and reset
    st.sidebar.markdown("### :material/warning: Varning")
    if st.sidebar.button('Radera hela databasen'):
        delete_feedback_and_reset_dashboard()

    st.sidebar.markdown(
        "####"
        )
    
    st.sidebar.markdown(f"""
            __Version:__ {c.app_version}  
            __Senast uppdaterad:__ {c.app_updated_date}       
                        """)
    

    ####################################
    ### MAIN PAGE

    topcol1, topcol2 = st.columns([14, 4], gap = "medium", vertical_alignment = "top")

    with topcol1:

        st.markdown(f"## :material/dashboard: {c.app_name} | Dashboard")

    with topcol2:

        today = datetime.now()
        first_of_month = today.replace(day=1)

        date_picker = st.date_input(
        "Välj datumintervall | Denna månad är förvald",
        (first_of_month, today),  # Default range: first of current month to today
        min_value=first_of_month,
        max_value=today,
        format="YYYY-MM-DD",
        label_visibility = "collapsed"
        )

        #st.write(date_picker)

    col1, col2, col3 = st.columns([7, 7, 4], gap = "medium", vertical_alignment = "top")
    
    # COL 1

    with col1:

        # Container IMAGE
        with st.container(border=False):

            image_container = st.empty()

            if 'image_url' in st.session_state and st.session_state.image_url:
                image_container.image(st.session_state.image_url)
            
            else:
                image_container.write("")  # Or handle the case where no image is present
        

        # Container "Läget på Indexator" - summarized imput
        with st.container(border=False):

            summarized_imput = st.empty()

            if 'summarize_user_input' in st.session_state:
                summarized_imput.markdown(st.session_state.summarize_user_input)

    

    # COL 2
    
    with col2:
            
        # Container "Ledarskap" - summarized input
        with st.container(border=True):
            
            container_summarize_leadership = st.empty()

            if 'summarize_leadership' in st.session_state:
                container_summarize_leadership.markdown(st.session_state.summarize_leadership)
                
            if not live_mode:

                def generate_recommendation():
                    summarize_leadership_recommendation = stream_text_openai(p.prompt_generate_recommendation, st.session_state.summarize_leadership, container_summarize_leadership_recommendation)
                    supabase.table('admin_dashboard').update({
                                    'summarize_leadership_recommendation': summarize_leadership_recommendation
                                }).eq('dashboard_id', st.session_state.dashboard_id).execute()
                
                with st.expander("Rekommendation", icon = ":material/help:"):
                    st.button(":material/play_circle: Skapa rekommendation", key = "01", type = "primary", on_click = generate_recommendation)
                    container_summarize_leadership_recommendation = st.empty()

                    if 'summarize_leadership_recommendation' in st.session_state:
                        container_summarize_leadership_recommendation.markdown(st.session_state.summarize_leadership_recommendation)
            else:
                st.write("")
                    

        
        # Container "Arbetsmiljö" - summarized input
        with st.container(border=True):

            container_summarize_work_environment = st.empty()

            if 'summarize_work_environment' in st.session_state:
                container_summarize_work_environment.markdown(st.session_state.summarize_work_environment)
            
            if not live_mode:

                def generate_recommendation():
                    summarize_work_environment_recommendation = stream_text_openai(p.prompt_generate_recommendation, st.session_state.summarize_work_environment, container_summarize_work_environment_recommendation)
                    supabase.table('admin_dashboard').update({
                                    'summarize_work_environment_recommendation': summarize_work_environment_recommendation
                                }).eq('dashboard_id', st.session_state.dashboard_id).execute()
                
                with st.expander("Rekommendation", icon = ":material/help:"):
                    st.button(":material/play_circle: Skapa rekommendation", key = "02", type = "primary", on_click = generate_recommendation)
                    container_summarize_work_environment_recommendation = st.empty()

                    if 'summarize_work_environment_recommendation' in st.session_state:
                        container_summarize_work_environment_recommendation.markdown(st.session_state.summarize_work_environment_recommendation)
            else:
                st.write("")


        
        # Container "Jämställdhet" - summarized input
        with st.container(border=True):

            container_summarize_equality = st.empty()

            if 'summarize_equality' in st.session_state:
                container_summarize_equality.markdown(st.session_state.summarize_equality)
            
            if not live_mode:

                def generate_recommendation():
                    summarize_equality_recommendation = stream_text_openai(p.prompt_generate_recommendation, st.session_state.summarize_equality, container_summarize_equality_recommendation)
                    supabase.table('admin_dashboard').update({
                                    'summarize_equality_recommendation': summarize_equality_recommendation
                                }).eq('dashboard_id', st.session_state.dashboard_id).execute()
                
                with st.expander("Rekommendation", icon = ":material/help:"):
                    st.button(":material/play_circle: Skapa rekommendation", key = "03", type = "primary", on_click = generate_recommendation)
                    container_summarize_equality_recommendation = st.empty()

                    if 'summarize_equality_recommendation' in st.session_state:
                        container_summarize_equality_recommendation.markdown(st.session_state.summarize_equality_recommendation)
            else:
                st.write("")

        
        # Container "Övrigt" - summarized input
        with st.container(border=True):

            container_summarize_misc = st.empty()

            if 'summarize_misc' in st.session_state:
                container_summarize_misc.markdown(st.session_state.summarize_misc)

            if not live_mode:

                def generate_recommendation():
                    summarize_misc_recommendation = stream_text_openai(p.prompt_generate_recommendation, st.session_state.summarize_misc, container_summarize_misc_recommendation)
                    supabase.table('admin_dashboard').update({
                                    'summarize_misc_recommendation': summarize_misc_recommendation
                                }).eq('dashboard_id', st.session_state.dashboard_id).execute()
                
                with st.expander("Rekommendation", icon = ":material/help:"):
                    st.button(":material/play_circle: Skapa rekommendation", key = "04", type = "primary", on_click = generate_recommendation)
                    container_summarize_misc_recommendation = st.empty()

                    if 'summarize_misc_recommendation' in st.session_state:
                        container_summarize_misc_recommendation.markdown(st.session_state.summarize_misc_recommendation)
            else:
                st.write("")
        

        # Container "Idéer" - summarized input
        with st.container(border=True):

            container_summarize_ideas = st.empty()

            if 'summarize_ideas' in st.session_state:
                container_summarize_ideas.markdown(st.session_state.summarize_ideas) 
            

    
    # COL 3
    
    with col3:

        col3_subcol1, col3_subcol2 = st.columns([2, 2], gap = "small", vertical_alignment = "top")

        
        with col3_subcol1:

            ### Container Workshop 
            container_dashboard_id = stylable_container(key = "column-1", css_styles = """
                    {
                    border: 0px solid rgba(255, 255, 255, 0.2);
                    background: rgb(17,77,110);
                    background: linear-gradient(124deg, rgb(24 24 24) 0%, rgb(37 37 37) 100%);
                    border-radius: 8px;
                    padding: 1rem 1rem 1rem 1rem;                                       
                    }
                    """)
            container_dashboard_id.caption("ID")

            if 'dashboard_id' in st.session_state:
                container_dashboard_id.markdown(f"# {st.session_state.dashboard_id}")


        with col3_subcol2:

            # Container Number of user entries
            container_user_entries = stylable_container(key = "column-2", css_styles = """
                    {
                    border: 0px solid rgba(255, 255, 255, 0.2);
                    background: rgb(17,77,110);
                    background: linear-gradient(124deg, rgb(24 24 24) 0%, rgb(37 37 37) 100%);
                    border-radius: 8px;
                    padding: 1rem 1rem 1rem 1rem;                                       
                    }
                                                            """)
            container_user_entries.caption("Svarande")
            entry_container = container_user_entries.empty()

        
        # Collected individual feedback
        with stylable_container(key = "column-3", css_styles = """
                {
                border: 0px solid rgba(255, 255, 255, 0.2);
                background: linear-gradient(124deg, rgb(24 24 24) 0%, rgb(37 37 37) 100%);
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
                            
                            new_entries = False

                            for record in reversed(records):
                                if not record.get('collected'):
                                    st.toast('Hooray! Nytt bidrag!', icon='🎉')

                                    # Update the record in the database
                                    supabase.table('feedback').update({'collected': "Done"}).eq('id', record['id']).execute()
                                    record['collected'] = "Done"  # Update the local record

                                    count_number_of_entries += 1

                                    new_entries = True
                            
                            for record in reversed(records):
                                if new_entries == True:
                                    
                                        
                                    # Process and summarize user input
                                    user_input = collect_user_input()
                                    summarize_user_input = stream_text_openai(p.prompt_summarize, user_input, summarized_imput)
                                    summarize_leadership = stream_text_openai(p.prompt_summarize_leadership, user_input, container_summarize_leadership)
                                    summarize_work_environment = stream_text_openai(p.prompt_summarize_work_environment, user_input, container_summarize_work_environment)
                                    summarize_equality = stream_text_openai(p.prompt_summarize_equality, user_input, container_summarize_equality)
                                    summarize_misc = stream_text_openai(p.prompt_summarize_misc, user_input, container_summarize_misc)
                                    summarize_ideas = stream_text_openai(p.prompt_summarize_ideas, user_input, container_summarize_ideas)
                                    
                                    image_prompt_to_dalle = process_text_openai_image_prompt(p.image_prompt, summarize_user_input, image_container)
                                    create_image_and_get_url = create_image(image_prompt_to_dalle, image_container)
                                    image_save_path_and_download = download_image(create_image_and_get_url, image_container)
                                    
                                    # Update the workshop_admin table with the latest values
                                    supabase.table('admin_dashboard').update({
                                        'summarize_user_input': summarize_user_input,
                                        'summarize_leadership': summarize_leadership,
                                        'summarize_work_environment': summarize_work_environment,
                                        'summarize_equality': summarize_equality,
                                        'summarize_misc': summarize_misc,
                                        'summarize_ideas': summarize_ideas,
                                        'image_url': image_save_path_and_download
                                    }).eq('dashboard_id', st.session_state.dashboard_id).execute() 

                                    new_entries = False

                                else:
                            
                                    entry_id = record['id']
                                    created_at = datetime.fromisoformat(record['created_at'])
                                    formatted_time = created_at.strftime('%Y-%m-%d | %H:%M')
                                    
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
