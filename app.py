# app.py
import streamlit as st
import spacy
from core_logic.parser import StatementParser # We'll reuse our parser
from core_logic.reasoner import SimpleLogicEngine # And our reasoner

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Logic Lab")
st.title("🧠 Logic Lab: Interactive Truth Engine")
st.markdown("A tool to build and test a transparent, controllable logic engine.")

# --- Initialize Session State ---
# Streamlit reruns the script on every interaction. We use session_state
# to keep our knowledge base and other data persistent across interactions.
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = []
if 'parser' not in st.session_state:
    # Load the spaCy model once and store it in session state
    try:
        st.session_state.parser = spacy.load("en_core_web_sm")
    except OSError:
        st.info("Downloading spaCy model 'en_core_web_sm'...")
        from spacy.cli import download
        download("en_core_web_sm")
        st.session_state.parser = spacy.load("en_core_web_sm")

# --- Sidebar: Input and Control ---
with st.sidebar:
    st.header("1. Add a Statement")
    new_statement = st.text_input("Enter a statement:", key="statement_input")
    
    if st.button("Parse and Evaluate"):
        if new_statement:
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
            
            # Now, run our simple parser to get the structured data
            # We'll create a simplified version here for the UI
            subject = None
            object = None
            negated = "neg" in [t.dep_ for t in doc]
            
            for token in doc:
                if token.dep_ == "nsubj":
                    subject = token.text.lower()
                if token.dep_ in ["attr", "acomp", "dobj"]:
                    object = token.text.lower()
            
            st.session_state.parsed_statement = {
                "subject": subject,
                "object": object,
                "negated": negated
            }

# --- Main Content Area ---

st.header("2. Parsing Details & Human Correction")

if 'current_parsing' in st.session_state:
    # Show the raw token-by-token analysis
    st.subheader("Token-by-Token Analysis")
    st.dataframe(st.session_state.current_parsing['tokens'], use_container_width=True)

    # Show the parsed statement and allow correction
    st.subheader("Parsed Statement (Correct if Needed)")
    parsed = st.session_state.parsed_statement
    
    # Use columns to lay out the input fields nicely
    col1, col2, col3 = st.columns(3)
    with col1:
        corrected_subject = st.text_input("Subject", value=parsed.get('subject', ''), key="correct_subject")
    with col2:
        corrected_object = st.text_input("Object", value=parsed.get('object', ''), key="correct_object")
    with col3:
        corrected_negated = st.checkbox("Negated", value=parsed.get('negated', False), key="correct_negated")
    
    if st.button("Commit to Knowledge Base"):
        final_fact = {
            "subject": corrected_subject.lower(),
            "object": corrected_object.lower(),
            "negated": corrected_negated,
            "original_text": st.session_state.current_parsing['text']
        }
        # Check for contradictions before adding
        contradiction_found = False
        for known_fact in st.session_state.knowledge_base:
            if (known_fact['subject'] == final_fact['subject'] and
                known_fact['object'] == final_fact['object'] and
                known_fact['negated'] != final_fact['negated']):
                st.error(f"🚨 CONTRADICTION DETECTED with: '{known_fact['original_text']}'")
                contradiction_found = True
                break
        
        if not contradiction_found:
            st.session_state.knowledge_base.append(final_fact)
            st.success(f"✅ Fact added: '{final_fact['original_text']}'")
            # Clear the parsing info to reset the UI
            del st.session_state.current_parsing
            del st.session_state.parsed_statement
            st.rerun()


st.header("3. Current Knowledge Base")

if not st.session_state.knowledge_base:
    st.info("The knowledge base is empty. Add a statement to begin.")
else:
    st.dataframe(st.session_state.knowledge_base, use_container_width=True)
