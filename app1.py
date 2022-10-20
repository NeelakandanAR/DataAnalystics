import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from pivottablejs import pivot_ui
import pandas as pd
import mysql.connector 

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    cnx = mysql.connector.connect(**st.secrets["mysql"])
    cursor = cnx.cursor(buffered=True)
    return cnx


conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT * from FEE_PAYMENTS_VW fpv;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")
