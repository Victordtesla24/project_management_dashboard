import streamlit as st
st.set_page_config(layout='wide')

"""Workflow management page."""

import time


st.title("Workflow Status")

if st.button("Run", key="run-workflow"):
    if "trigger_error" in st.experimental_get_query_params():
        st.markdown('<div data-testid="stErrorMessage">', unsafe_allow_html=True)
        st.error("Error in workflow")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Running..."):
            time.sleep(2)
            st.markdown('<div data-testid="stSuccessMessage">', unsafe_allow_html=True)
            st.success("Workflow Complete")
            st.markdown('</div>', unsafe_allow_html=True)
