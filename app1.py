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
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("select * from FEE_PAYMENTS_VW;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")
# 2. horizontal menu
selected = option_menu(None, ["Home", "Upload", 'Settings'], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
selected

if selected == "Home":
    st.title(f"You have selected {selected}")
if selected == "Upload":
    st.title(f"You have selected {selected}")
    uploaded_file = st.file_uploader("Upload your input file", type=['csv'], key="uploaded_file")

    st.title(f"You have selected {selected}")
    iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
    st.header('**CSK Academy Data analytics**')
    
    option_list = ['original table','no of stndts',  'Gender', 'age category']
    result = st.selectbox('select your analysis category', option_list)
    ##iris = pd.read_table(uploaded_file)
    col = iris.columns.to_list()
    iris.columns = col
    if result == 'original table':
        st.info("Original table")
        st.write(iris.head())
    
    iris['invoiceDate']= pd.to_datetime(iris['invoiceDate'])
    iris['invoiceDate']= pd.to_datetime(iris['invoiceDate'], format='%y%m%d')
    iris['Month'] = pd.to_datetime(iris['invoiceDate']).dt.month_name()
    iris = iris[['userId','AgeBucket', 'invoiceDate', 'gender', 'courseId', 'fee', 'AcademyName', 'courseDurationInMonths','itemDescription'
          ,'amount','Month']]
    chennai = iris[iris['AcademyName']=='SKA Chennai']
    Salem = iris[iris['AcademyName']=='SKA Salem']
    
    #st.info("null values in each column")
    st.write(iris.isna().sum())

# finding the month wise count and amount in each academy
    if result == 'no of stndts':
        
        st.header('**No of students and the fee collected in each academy**')

        b = pd.DataFrame(iris.groupby(['Month','AcademyName']).agg({'userId':['count'],'amount':['sum']})).reset_index()
        b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
        b1 = b.pivot(index=['Month_','AcademyName_'], columns=[], values=['userId_count','amount_sum'])
        b1.columns = ['userId_count','amount']
        b1.index.names = ['Month','AcademyName']
        b1 = b1.rename(index={'SKA Chennai':'Chennai','SKA Salem':'Salem'})
        convert_dict = {'userId_count': int,
                                            }
        b1= b1.astype(convert_dict)
        st.write(b1)
        
### Gender wise count in each academy
    if result == 'Gender':
        iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
        chennai = iris[iris['AcademyName']=='SKA Chennai']
        Salem = iris[iris['AcademyName']=='SKA Salem']
        st.header('**Gender wise count in each academy**')
        st.info("Chennai")
#         chennai = df1[df1['AcademyName']=='SKA Chennai']
        b = pd.DataFrame(chennai.groupby(['Month','gender']).agg({'userId':['count']})).reset_index()
        b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
        b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
        b1.columns = ['Female', 'Male']
        b1.index.name = 'Month'
        b1.fillna(0,inplace=True)
        st.write(b1)
#         Salem = df1[df1['AcademyName']=='SKA Salem']
        st.info("Salem")
        b = pd.DataFrame(Salem.groupby(['Month','gender']).agg({'userId':['count']})).reset_index()
        b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
        b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
        b1.columns = ['Female', 'Male']
        b1.index.name = 'Month'
        b1.fillna(0,inplace=True)
        st.dataframe(b1)

### The age category of the students registered in the respective academies
    if result == 'age category':
        iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
        chennai = iris[iris['AcademyName']=='SKA Chennai']
        Salem = iris[iris['AcademyName']=='SKA Salem']
        st.header('**The age category of the students registered in the respective academies**')
        st.info("Chennai")
        b = pd.DataFrame(chennai.groupby(['AgeBucket','Month']).agg({'userId':['count','nunique']})).reset_index()
        b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
        b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
        # b1.columns = ['Chennai', 'Salem']
        b1.index.name = 'Age Bucket'
        st.dataframe(b1)

        st.info("Salem")
        b = pd.DataFrame(Salem.groupby(['AgeBucket','Month']).agg({'userId':['count','nunique']})).reset_index()
        b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
        b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
        # b1.columns = ['Chennai', 'Salem']
        b1.index.name = 'Age Bucket'
        st.dataframe(b1)
if selected == "Settings":
    st.title(f"You have selected {selected}")    
