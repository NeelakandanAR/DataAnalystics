import streamlit as st
import numpy as np
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from pivottablejs import pivot_ui
import pandas as pd
import mysql.connector
import altair as alt
import pickle
from pathlib import Path

import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

# Security
# passlib,hashlib,bcrypt,scrypt
import hashlib


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


# DB Management
import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()


# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


def main():
    """Simple Login App"""

    st.title("Simple Login App")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:
                st.success("Logged In as {}".format(username))
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

                # rows = run_query("SELECT * from FEE_PAYMENTS_VW fpv;")
                df1 = pd.read_sql('SELECT * from FEE_PAYMENTS_VW', con=conn)
                # df = pd.DataFrame(rows)
                # st.write(df)
                # st.write(df1)
                # Difine Dict with the key-value pair to remap.
                # d = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}

                iris = pd.DataFrame(df1)
                # iris=iris.replace({"Month": d},inplace=True)
                st.header('**CSK Academy Data analytics**')

                option_list = ['no of stndts', 'Gender', 'age category', 'Course duration',
                               'Weekend/Weekday preferences']
                result = st.selectbox('select your analysis category', option_list)
                ##iris = pd.read_table(uploaded_file)
                col = iris.columns.to_list()
                iris.columns = col
                iris['invoiceDate'] = pd.to_datetime(iris['invoiceDate'])
                iris['invoiceDate'] = pd.to_datetime(iris['invoiceDate'], format='%y%m%d')
                iris['Month'] = pd.to_datetime(iris['invoiceDate']).dt.month_name()
                iris = iris[['userId', 'AgeBucket', 'invoiceDate', 'gender', 'courseId', 'fee', 'AcademyName',
                             'courseDurationInMonths', 'itemDescription', 'type'
                    , 'amount', 'Month']]
                # chennai = iris[iris['AcademyName']=='SKA Chennai']
                # Salem = iris[iris['AcademyName']=='SKA Salem']

                # finding the month wise count and amount in each academy

                start = st.date_input('Start', value=pd.to_datetime('2018-01-01'))
                start = pd.to_datetime(start)
                end = st.date_input('End', value=pd.to_datetime('today'))
                end = pd.to_datetime(end)
                iri = iris[(iris['invoiceDate'] > start) & (iris['invoiceDate'] < end)]
                if result == 'no of stndts':
                    st.header('**No of students and the fee collected in each academy**')

                    #     b = pd.DataFrame(iris.groupby(['Month','AcademyName']).agg({'userId':['count']})).reset_index()
                    #     b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
                    #     b1 = iris.pivot(index=['Month'], columns=['AcademyName'], values=['userId'], aggfunc='count')
                    #     b1 = iris.pivot_table('userId', index='Month', columns='AcademyName', aggfunc='count')
                    #     b1.columns = ['userId_count']
                    #     b1.index.names = ['Month','AcademyName']
                    #     b1 = b1.rename(index={'SKA Chennai':'Chennai','SKA Salem':'Salem'})
                    #     convert_dict = {'userId_count': int}
                    #     b1= b1.astype(convert_dict)

                    #     b2 = iris.pivot_table('fee', index='Month', columns='AcademyName', aggfunc='sum')
                    #     st.write(b2)

                    #     b1 = iri.pivot_table('userId', index='Month', columns='AcademyName', aggfunc='count')
                    #     b2 = iri.pivot_table('fee', index='Month', columns='AcademyName', aggfunc='sum')
                    # #     st.write(b1)

                    #     st.bar_chart(b1)

                    #     st.bar_chart(b2)

                    b1 = alt.Chart(iri).mark_bar().encode(
                        x='month(invoiceDate):O',
                        y='count(userId):Q',
                        color='AcademyName:N',
                        column='AcademyName:N').properties(width=300, height=400)
                    st.info("Student count")
                    st.altair_chart(b1)

                    b2 = alt.Chart(iri).mark_bar().encode(
                        x='month(invoiceDate):O',
                        y='sum(fee):Q',
                        color='AcademyName:N',
                        column='AcademyName:N').properties(width=300, height=400)
                    st.info("Fee collected")
                    st.altair_chart(b2)

                #     np.round(pd.pivot_table(b, values='userId',
                #                             index=['Month'],
                #                             columns=['AcademyName'],
                #                             aggfunc=lambda userId: len(userId.unique())),
                #                             fill_value=0),2).plot.barh(figsize=(10,7),
                #                                                       title='Mean car price by make and number of doors')

                ### Gender wise count in each academy
                if result == 'Gender':
                    #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
                    chennai = iri[iri['AcademyName'] == 'SKA Chennai']
                    Salem = iri[iri['AcademyName'] == 'SKA Salem']
                    st.header('**Gender wise count in each academy**')
                    st.info("Chennai")
                    #         chennai = df1[df1['AcademyName']=='SKA Chennai']
                    b = pd.DataFrame(chennai.groupby(['Month', 'gender']).agg({'userId': ['count']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
                    b1.columns = ['Female', 'Male']
                    b1.index.name = 'Month'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.write(b1)
                    #         Salem = df1[df1['AcademyName']=='SKA Salem']
                    st.info("Salem")
                    b = pd.DataFrame(Salem.groupby(['Month', 'gender']).agg({'userId': ['count']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
                    b1.columns = ['Female', 'Male']
                    b1.index.name = 'Month'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)

                ### The age category of the students registered in the respective academies
                if result == 'age category':
                    #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
                    chennai = iri[iri['AcademyName'] == 'SKA Chennai']
                    Salem = iri[iri['AcademyName'] == 'SKA Salem']
                    st.header('**The age category of the students registered in the respective academies**')
                    st.info("Chennai")
                    b = pd.DataFrame(
                        chennai.groupby(['AgeBucket', 'Month']).agg({'userId': ['count', 'nunique']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
                    # b1.columns = ['Chennai', 'Salem']
                    b1.index.name = 'Age Bucket'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)

                    st.info("Salem")
                    b = pd.DataFrame(
                        Salem.groupby(['AgeBucket', 'Month']).agg({'userId': ['count', 'nunique']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
                    # b1.columns = ['Chennai', 'Salem']
                    b1.index.name = 'Age Bucket'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)

                if result == 'Course duration':
                    #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
                    chennai = iri[iri['AcademyName'] == 'SKA Chennai']
                    Salem = iri[iri['AcademyName'] == 'SKA Salem']
                    st.header('**Course duration of the students registered in the respective academies**')
                    st.info("Chennai")
                    b = pd.DataFrame(chennai.groupby(['courseDurationInMonths', 'Month']).agg(
                        {'userId': ['count', 'nunique']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='courseDurationInMonths_', columns='Month_', values='userId_nunique')
                    # b1.columns = ['Chennai', 'Salem']
                    b1.index.name = 'Course Duration'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)

                    st.info("Salem")
                    b = pd.DataFrame(Salem.groupby(['courseDurationInMonths', 'Month']).agg(
                        {'userId': ['count', 'nunique']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='courseDurationInMonths_', columns='Month_', values='userId_nunique')
                    # b1.columns = ['Chennai', 'Salem']
                    b1.index.name = 'Course Duration'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)

                if result == 'Weekend/Weekday preferences':
                    #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
                    chennai = iri[iri['AcademyName'] == 'SKA Chennai']
                    Salem = iri[iri['AcademyName'] == 'SKA Salem']
                    st.header('**Weekend/Weekday preferences of the students registered in the respective academies**')
                    st.info("Chennai")
                    b = pd.DataFrame(
                        chennai.groupby(['type', 'Month']).agg({'userId': ['count', 'nunique']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='type_', columns='Month_', values='userId_nunique')
                    # b1.columns = ['Chennai', 'Salem']
                    b1.index.name = 'Weekend/Weekday preferences'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)

                    st.info("Salem")
                    b = pd.DataFrame(
                        Salem.groupby(['type', 'Month']).agg({'userId': ['count', 'nunique']})).reset_index()
                    b.columns = b.columns.get_level_values(0) + '_' + b.columns.get_level_values(1)
                    b1 = b.pivot(index='type_', columns='Month_', values='userId_nunique')
                    # b1.columns = ['Chennai', 'Salem']
                    b1.index.name = 'Weekend/Weekday preferences'
                    b1.fillna(0, inplace=True)
                    b1 = b1.astype(int)
                    st.dataframe(b1)
                else:
                    st.warning("Incorrect Username/Password")

elif choice == "SignUp":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')

if st.button("Signup"):
    create_usertable()
    add_userdata(new_user, make_hashes(new_password))
    st.success("You have successfully created a valid Account")
    st.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()

        
        
        
        
        
        
        
        
#         import streamlit as st
# import numpy as np
# import streamlit.components.v1 as components
# from streamlit_option_menu import option_menu
# from pivottablejs import pivot_ui
# import pandas as pd
# import mysql.connector 
# import altair as alt
# import pickle
# from pathlib import Path

# import streamlit as st  # pip install streamlit
# import streamlit_authenticator as stauth  # pip install streamlit-authenticator


# # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
# st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")


# # --- USER AUTHENTICATION ---
# names = ["Peter Parker", "Rebecca Miller"]
# usernames = ["pparker", "rmiller"]

# # load hashed passwords
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("rb") as file:
#     hashed_passwords = pickle.load(file)

# authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
#     "sales_dashboard", "abcdef")

# name, authentication_status, username = authenticator.login("Login", "main")

# if authentication_status == False:
#     st.error("Username/password is incorrect")

# if authentication_status == None:
#     st.warning("Please enter your username and password")

# if authentication_status:
#     # Initialize connection.
#     # Uses st.experimental_singleton to only run once.
#     @st.experimental_singleton
#     def init_connection():
#         return mysql.connector.connect(**st.secrets["mysql"])

#     conn = init_connection()



#     # Perform query.
#     # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
#     @st.experimental_memo(ttl=600)
#     def run_query(query):
#         with conn.cursor() as cur:
#             cur.execute(query)
#             return cur.fetchall()

#     # rows = run_query("SELECT * from FEE_PAYMENTS_VW fpv;")
#     df1 = pd.read_sql('SELECT * from FEE_PAYMENTS_VW', con=conn)
#     # df = pd.DataFrame(rows)
#     # st.write(df)
#     # st.write(df1)
#     # Difine Dict with the key-value pair to remap.
#     # d = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}


#     iris = pd.DataFrame(df1)
#     # iris=iris.replace({"Month": d},inplace=True)
#     st.header('**CSK Academy Data analytics**')

#     option_list = ['no of stndts',  'Gender', 'age category', 'Course duration', 'Weekend/Weekday preferences']
#     result = st.selectbox('select your analysis category', option_list)
#     ##iris = pd.read_table(uploaded_file)
#     col = iris.columns.to_list()
#     iris.columns = col
#     iris['invoiceDate']= pd.to_datetime(iris['invoiceDate'])
#     iris['invoiceDate']= pd.to_datetime(iris['invoiceDate'], format='%y%m%d')
#     iris['Month'] = pd.to_datetime(iris['invoiceDate']).dt.month_name()
#     iris = iris[['userId','AgeBucket', 'invoiceDate', 'gender', 'courseId', 'fee', 'AcademyName', 'courseDurationInMonths','itemDescription','type'
#           ,'amount','Month']]
#     # chennai = iris[iris['AcademyName']=='SKA Chennai']
#     # Salem = iris[iris['AcademyName']=='SKA Salem']

#     # finding the month wise count and amount in each academy

#     start = st.date_input('Start', value = pd.to_datetime('2018-01-01'))
#     start = pd.to_datetime(start)
#     end = st.date_input('End', value = pd.to_datetime('today'))
#     end = pd.to_datetime(end)
#     iri = iris[(iris['invoiceDate'] > start) & (iris['invoiceDate'] < end)]
#     if result == 'no of stndts':

#         st.header('**No of students and the fee collected in each academy**')

#     #     b = pd.DataFrame(iris.groupby(['Month','AcademyName']).agg({'userId':['count']})).reset_index()
#     #     b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#     #     b1 = iris.pivot(index=['Month'], columns=['AcademyName'], values=['userId'], aggfunc='count')
#     #     b1 = iris.pivot_table('userId', index='Month', columns='AcademyName', aggfunc='count')
#     #     b1.columns = ['userId_count']
#     #     b1.index.names = ['Month','AcademyName']
#     #     b1 = b1.rename(index={'SKA Chennai':'Chennai','SKA Salem':'Salem'})
#     #     convert_dict = {'userId_count': int}
#     #     b1= b1.astype(convert_dict)

#     #     b2 = iris.pivot_table('fee', index='Month', columns='AcademyName', aggfunc='sum')
#     #     st.write(b2)

#     #     b1 = iri.pivot_table('userId', index='Month', columns='AcademyName', aggfunc='count')
#     #     b2 = iri.pivot_table('fee', index='Month', columns='AcademyName', aggfunc='sum')
#     # #     st.write(b1)


#     #     st.bar_chart(b1)

#     #     st.bar_chart(b2)



#         b1 = alt.Chart(iri).mark_bar().encode(
#         x='month(invoiceDate):O',
#         y='count(userId):Q',
#         color='AcademyName:N',
#         column='AcademyName:N').properties(width=300, height=400)
#         st.info("Student count")
#         st.altair_chart(b1)


#         b2 = alt.Chart(iri).mark_bar().encode(
#         x='month(invoiceDate):O',
#         y='sum(fee):Q',
#         color='AcademyName:N',
#         column='AcademyName:N').properties(width=300, height=400)
#         st.info("Fee collected")
#         st.altair_chart(b2)


#     #     np.round(pd.pivot_table(b, values='userId', 
#     #                             index=['Month'], 
#     #                             columns=['AcademyName'], 
#     #                             aggfunc=lambda userId: len(userId.unique())),
#     #                             fill_value=0),2).plot.barh(figsize=(10,7),
#     #                                                       title='Mean car price by make and number of doors')

#     ### Gender wise count in each academy
#     if result == 'Gender':
#     #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
#         chennai = iri[iri['AcademyName']=='SKA Chennai']
#         Salem = iri[iri['AcademyName']=='SKA Salem']
#         st.header('**Gender wise count in each academy**')
#         st.info("Chennai")
#     #         chennai = df1[df1['AcademyName']=='SKA Chennai']
#         b = pd.DataFrame(chennai.groupby(['Month','gender']).agg({'userId':['count']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
#         b1.columns = ['Female', 'Male']
#         b1.index.name = 'Month'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.write(b1)
#     #         Salem = df1[df1['AcademyName']=='SKA Salem']
#         st.info("Salem")
#         b = pd.DataFrame(Salem.groupby(['Month','gender']).agg({'userId':['count']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='Month_', columns='gender_', values='userId_count')
#         b1.columns = ['Female', 'Male']
#         b1.index.name = 'Month'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)

#     ### The age category of the students registered in the respective academies
#     if result == 'age category':
#     #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
#         chennai = iri[iri['AcademyName']=='SKA Chennai']
#         Salem = iri[iri['AcademyName']=='SKA Salem']
#         st.header('**The age category of the students registered in the respective academies**')
#         st.info("Chennai")
#         b = pd.DataFrame(chennai.groupby(['AgeBucket','Month']).agg({'userId':['count','nunique']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
#         # b1.columns = ['Chennai', 'Salem']
#         b1.index.name = 'Age Bucket'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)

#         st.info("Salem")
#         b = pd.DataFrame(Salem.groupby(['AgeBucket','Month']).agg({'userId':['count','nunique']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='AgeBucket_', columns='Month_', values='userId_nunique')
#         # b1.columns = ['Chennai', 'Salem']
#         b1.index.name = 'Age Bucket'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)


#     if result == 'Course duration':
#     #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
#         chennai = iri[iri['AcademyName']=='SKA Chennai']
#         Salem = iri[iri['AcademyName']=='SKA Salem']
#         st.header('**Course duration of the students registered in the respective academies**')
#         st.info("Chennai")
#         b = pd.DataFrame(chennai.groupby(['courseDurationInMonths','Month']).agg({'userId':['count','nunique']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='courseDurationInMonths_', columns='Month_', values='userId_nunique')
#         # b1.columns = ['Chennai', 'Salem']
#         b1.index.name = 'Course Duration'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)

#         st.info("Salem")
#         b = pd.DataFrame(Salem.groupby(['courseDurationInMonths','Month']).agg({'userId':['count','nunique']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='courseDurationInMonths_', columns='Month_', values='userId_nunique')
#         # b1.columns = ['Chennai', 'Salem']
#         b1.index.name = 'Course Duration'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)


#     if result == 'Weekend/Weekday preferences':
#     #     iris = pd.read_table(st.session_state["uploaded_file"] , sep=",", header=0)
#         chennai = iri[iri['AcademyName']=='SKA Chennai']
#         Salem = iri[iri['AcademyName']=='SKA Salem']
#         st.header('**Weekend/Weekday preferences of the students registered in the respective academies**')
#         st.info("Chennai")
#         b = pd.DataFrame(chennai.groupby(['type','Month']).agg({'userId':['count','nunique']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='type_', columns='Month_', values='userId_nunique')
#         # b1.columns = ['Chennai', 'Salem']
#         b1.index.name = 'Weekend/Weekday preferences'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)

#         st.info("Salem")
#         b = pd.DataFrame(Salem.groupby(['type','Month']).agg({'userId':['count','nunique']})).reset_index()
#         b.columns = b.columns.get_level_values(0) + '_' +  b.columns.get_level_values(1)
#         b1 = b.pivot(index='type_', columns='Month_', values='userId_nunique')
#         # b1.columns = ['Chennai', 'Salem']
#         b1.index.name ='Weekend/Weekday preferences'
#         b1.fillna(0, inplace=True)
#         b1 = b1.astype(int)
#         st.dataframe(b1)






