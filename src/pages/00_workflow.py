import streamlit as st
st.set_page_config(layout='wide')

"""Workflow management page."""

import time


st.title("Workflow Status")

if st.button("Run"):
    if "trigger_error" in st.experimental_get_query_params():
        st.error("Error in workflow")
    else:
        with st.spinner("Running..."):
            time.sleep(2)
            st.success("Workflow Complete")
