import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from pivottablejs import pivot_ui
import pandas as pd

import streamlit as st
import pandas as pd

# 2. horizontal menu
selected = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
selected

if selected == "Home":
    st.title(f"You have selected {selected}")
if selected == "Upload":
    st.title(f"You have selected {selected}")
    uploaded_file = st.file_uploader("Upload your input file", type=['csv'])
#if selected == "Tasks":
    #st.title(f"You have selected {selected}")
    ### Read csv
    iris = pd.read_table(uploaded_file , sep=',', header=0)
    st.header('**CSK Academy Data analytics**')
 
    
    ##iris = pd.read_table(uploaded_file)
    col = iris.columns.to_list()
    iris.columns = col
    st.info("Original table")
    st.write(iris.head())
    df1=iris
    df1['invoiceDate']= pd.to_datetime(df1['invoiceDate'])
    df1['invoiceDate']= pd.to_datetime(df1['invoiceDate'], format='%y%m%d')
    df1['Month'] = pd.to_datetime(df1['invoiceDate']).dt.month_name()
    df1 = iris[['userId','AgeBucket', 'invoiceDate', 'gender', 'courseId', 'fee', 'AcademyName', 'courseDurationInMonths','itemDescription'
          ,'amount','Month']]
    #st.info("null values in each column")
    #st.write(df1.isna().sum())

# finding the month wise count and amount in each academy
    st.header('**No of students and the fee collected in each academy**')
    
    b = pd.DataFrame(df1.groupby(['Month','AcademyName']).agg({'userId':['count'],'amount':['sum']})).reset_index()
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
    st.header('**Gender wise count in each academy**')
    st.info("Chennai")
    chennai = df1[df1['AcademyName']=='SKA Chennai']
    b = pd.DataFrame(chennai.groupby(['Month','gender']).agg({'userId':['count']})).reset_index()
    b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
    b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
    b1.columns = ['Female', 'Male']
    b1.index.name = 'Month'
    b1.fillna(0,inplace=True)
    st.write(b1)
    Salem = df1[df1['AcademyName']=='SKA Salem']
    st.info("Salem")
    b = pd.DataFrame(Salem.groupby(['Month','gender']).agg({'userId':['count']})).reset_index()
    b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
    b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
    b1.columns = ['Female', 'Male']
    b1.index.name = 'Month'
    b1.fillna(0,inplace=True)
    st.write(b1)

### The age category of the students registered in the respective academies
    st.header('**The age category of the students registered in the respective academies**')
    st.info("Chennai")
    b = pd.DataFrame(chennai.groupby(['AgeBucket','Month']).agg({'userId':['count','nunique']})).reset_index()
    b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
    b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
    # b1.columns = ['Chennai', 'Salem']
    b1.index.name = 'Age Bucket'
    st.write(b1)

    st.info("Salem")
    b = pd.DataFrame(Salem.groupby(['AgeBucket','Month']).agg({'userId':['count','nunique']})).reset_index()
    b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
    b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
    # b1.columns = ['Chennai', 'Salem']
    b1.index.name = 'Age Bucket'
    st.write(b1)
if selected == "Settings":
    st.title(f"You have selected {selected}")    
