import streamlit as st
import os
from chatbot_manager import ChatbotManager

# Set up Streamlit page configuration
st.set_page_config(page_title="Chatbot Application", layout="wide")

# Session state to hold chatbot manager and messages
if 'chatbot_manager' not in st.session_state:
    st.session_state['chatbot_manager'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'query_bar' not in st.session_state:
    st.session_state['query_bar'] = ""

# Title of the application
st.title("Chatbot Application")

# File uploader for PDF and DOCX files
uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

# Directory to temporarily store uploaded files
temp_folder_path = "temp_files"
if not os.path.exists(temp_folder_path):
    os.makedirs(temp_folder_path)

# Load documents and initialize the chatbot manager
if uploaded_files:
    for uploaded_file in uploaded_files:
        with open(os.path.join(temp_folder_path, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    # Initialize the ChatbotManager with the temp folder path
    st.session_state['chatbot_manager'] = ChatbotManager(temp_folder_path)
    st.session_state['chatbot_manager'].load_and_split_documents()
    st.session_state['messages'].append({"role": "Bot", "content": "Documents loaded and ready for querying."})

# User input for queries
st.session_state.query_bar = st.text_input("Ask a question or type 'exit' to close the session:", st.session_state.query_bar)

# Process user input and generate responses
if st.session_state.query_bar:
    if st.session_state['chatbot_manager']:
        response = st.session_state['chatbot_manager'].get_response(st.session_state.query_bar)
        st.session_state['messages'].append({"role": "User ", "content": st.session_state.query_bar})
        if response:
            st.session_state['messages'].append({"role": "Bot", "content": response})
    else:
        st.session_state['messages'].append({"role": "Bot", "content": "Please upload documents first."})

    # Clear the query bar after generating a response
    st.session_state.query_bar = ""

# Display the conversation history
if st.session_state['messages']:
    for msg in st.session_state['messages']:
        if msg['role'] == 'User ':
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

# Clean up temporary files after the session ends
if st.button("Clear Session"):
    for filename in os.listdir(temp_folder_path):
        file_path = os.path.join(temp_folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    st.session_state['messages'] = []
    st.session_state['chatbot_manager'] = None
    st.session_state.query_bar = ""
    st.success("Session cleared. You can upload new documents.")