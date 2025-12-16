# app.py
import streamlit as st
import spacy
from core_logic.contextual_engine import ContextualLogicEngine # Use the new contextual engine

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Logic Lab")
st.title("🧠 Logic Lab: Interactive Truth Engine")
st.markdown("A tool to build and test a transparent, controllable logic engine.")

# --- Initialize Session State ---
# Streamlit reruns the script on every interaction. We use session_state
# to keep our knowledge base and other data persistent across interactions.
if 'contextual_engine' not in st.session_state:
    st.session_state.contextual_engine = ContextualLogicEngine()
if 'parser' not in st.session_state:
    # Load the spaCy model once and store it in session state
    try:
        st.session_state.parser = spacy.load("en_core_web_sm")
    except OSError:
        st.info("Downloading spaCy model 'en_core_web_sm'...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        st.session_state.parser = spacy.load("en_core_web_sm")

# --- Sidebar: Input and Control ---
with st.sidebar:
    st.header("1. Add a Statement")
    new_statement = st.text_input("Enter a statement:", key="statement_input")
    
    if st.button("Parse and Evaluate"):
        if new_statement:
            # Process the statement using the contextual engine
            st.session_state.contextual_engine.process_statement(new_statement)
            
            # We'll parse the statement and store the raw result in session state
            # for display and potential correction.
            doc = st.session_state.parser(new_statement)
            
            # Store the detailed parsing info for the user to see
            parsing_details = {
                "text": new_statement,
                "tokens": [
                    {"text": token.text, "lemma": token.lemma_, "pos": token.pos_, "dep": token.dep_}
                    for token in doc
                ]
            }
            st.session_state.current_parsing = parsing_details
            
            # Get the parsed result from the contextual engine
            parsed = st.session_state.contextual_engine._parse_statement(new_statement)
            if parsed:
                st.session_state.parsed_statement = parsed
            else:
                st.session_state.parsed_statement = {
                    "subject": None,
                    "object": None,
                    "negated": False
                }

# --- Main Content Area ---

st.header("2. Parsing Details & Human Correction")

if 'current_parsing' in st.session_state:
    # Show the raw token-by-token analysis
    st.subheader("Token-by-Token Analysis")
    st.dataframe(st.session_state.current_parsing['tokens'], use_container_width=True)

    # Show the parsed statement
    st.subheader("Parsed Statement")
    parsed = st.session_state.parsed_statement
    
    # Use columns to lay out the parsed info nicely
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Subject", value=parsed.get('subject', 'None'), disabled=True)
    with col2:
        st.text_input("Object", value=parsed.get('object', 'None'), disabled=True)
    with col3:
        st.checkbox("Negated", value=parsed.get('negated', False), disabled=True)
    
    st.info("✅ Statement automatically processed and added to conversation memory.")


st.header("3. Conversation Context")

# Get conversation summary from the contextual engine
summary = st.session_state.contextual_engine.get_conversation_summary()

if summary['total_statements'] == 0:
    st.info("No statements processed yet. Add a statement to begin.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Statements", summary['total_statements'])
    with col2:
        st.metric("Entities Tracked", summary['entities_tracked'])
    
    st.subheader("Recent Context")
    if summary['recent_context']:
        for i, stmt in enumerate(summary['recent_context'], 1):
            st.write(f"{i}. {stmt}")
    
    st.subheader("Entity States")
    if summary['entity_states']:
        for entity_name, entity_attrs in summary['entity_states'].items():
            with st.expander(f"📝 {entity_name.title()}"):
                for attr, value in entity_attrs.items():
                    if not attr.startswith('_'):  # Skip private attributes
                        st.write(f"• {attr}: {value}")
