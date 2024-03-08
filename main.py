
# import commands below download a few python libs 

# streamlit as st for connviencnce
import streamlit as st
from streamlit import selectbox
import pandas as pd
from PIL import Image
import sqlite3
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



IMAGES_FOLDER = "images"
#sets up connection with the database
conn = sqlite3.connect("drug_data.db", check_same_thread=False)

# creates a cursor object to execute sql queries on the sqlite db
c = conn.cursor()


# '''
# The following few functions contain the schema
# of our datebase, it is a good practice to keep
# the schemas in the scrpt itself to make it..
# -> modular
# -> simplified deployment
# -> Ease of testing
# '''

def create_customer_table():
    c.execute('''CREATE TABLE IF NOT EXISTS Customers(
                    C_Name VARCHAR(50) NOT NULL,
                    C_Password VARCHAR(50) NOT NULL,
                    C_Email VARCHAR(50) PRIMARY KEY NOT NULL,
                    C_State VARCHAR(50) NOT NULL,
                    C_Number VARCHAR(50) NOT NULL
                    )''')
    print('Customer Table created successfully')


def add_customer_data(Cname, Cpass, Cemail, Cstate, Cnumber):
    try:
        c.execute('''INSERT INTO Customers (C_Name, C_Password, C_Email, C_State, C_Number)
                     VALUES (?, ?, ?, ?, ?)''', (Cname, Cpass, Cemail, Cstate, Cnumber))
        conn.commit()
        send_welcome_email(Cemail)
        st.success("Account Created!")
        st.info("Go to the Login Menu to login")
    except sqlite3.Error as e:
        conn.rollback()
        st.error(f"Error inserting data into the database: {e}")

    conn.commit()
    send_welcome_email(Cemail)


def view_all_customer_data():
    return c.execute('SELECT * FROM Customers').fetchall()


def update_customer(Cemail, Cnumber):
    c.execute(
        '''UPDATE Customers
           SET C_Number = ?
           WHERE C_Email = ?''',
        (Cnumber, Cemail,))
    conn.commit()
    print("Updating")


def delete_customer(Cemail):
    c.execute(''' DELETE FROM Customers WHERE C_Email = ?''', (Cemail,))
    conn.commit()


def update_drug(Duse, Did):
    c.execute(''' UPDATE Drugs SET D_Use = ? WHERE D_id = ?''', (Duse, Did))
    conn.commit()


def delete_drug(Did):
    c.execute(''' DELETE FROM Drugs WHERE D_id = ?''', (Did,))
    conn.commit()


def create_drug_table():
    c.execute('''CREATE TABLE IF NOT EXISTS Drugs(
                D_Name VARCHAR(50) NOT NULL,
                D_ExpDate DATE NOT NULL,
                D_Use VARCHAR(50) NOT NULL,
                D_Qty INT NOT NULL,
                D_Price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                D_id INT PRIMARY KEY NOT NULL,
                D_Image_Path VARCHAR(255))
                ''')
    print('Drug Table created successfully')


def add_drug_data(Dname, Dexpdate, Duse, Dqty, DPrice, Did, image_path):
    c.execute('''INSERT INTO Drugs
                 (D_Name, D_Expdate, D_Use, D_Qty,D_Price, D_id,D_image_path)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (Dname, Dexpdate, Duse, Dqty, Dprice , Did, image_path))
    conn.commit()


def view_all_drug_data():
    return c.execute('SELECT * FROM Drugs').fetchall()


def create_order_table():
    c.execute('''
        CREATE TABLE IF NOT EXISTS Orders(
                O_Name VARCHAR(100) NOT NULL,
                O_Items VARCHAR(100) NOT NULL,
                O_Qty VARCHAR(100) NOT NULL,
                O_TotalPrice DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                O_id VARCHAR(100) PRIMARY KEY NOT NULL)
    ''')


def delete_order(Oid):
    c.execute(''' DELETE FROM Orders WHERE O_id = ?''', (Oid,))
    conn.commit()
    
def fetch_drug_price(drug_name):
    result = c.execute('SELECT D_Price FROM Drugs WHERE D_Name = ?', (drug_name,)).fetchone()
    return result[0] if result else 0.00

def calculate_total_price(items, quantities):
    item_list = items.split(',')
    qty_list = quantities.split(',')
    prices = [fetch_drug_price(item) for item in item_list]
    total_price = sum([float(price) * int(qty) for price, qty in zip(prices, qty_list)])
    return total_price 




def add_order_data(O_Name, O_Items, O_Qty, O_TotalPrice, O_id):
    c.execute('''
        INSERT INTO Orders (O_Name, O_Items, O_Qty, O_TotalPrice, O_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (O_Name, O_Items, O_Qty, O_TotalPrice, O_id))
    conn.commit()



def view_order_data(customer_name):
    return c.execute(
        'SELECT * FROM Orders WHERE O_Name = ?',
        (customer_name,)
    ).fetchall()


def view_all_order_data():
    return c.execute('SELECT * FROM Orders').fetchall()


#email notificatin code

def send_email_notification(recipient, subject, message):
    sender_email = "indrranil7@gmail.com"
    sender_password = "ipkj abkl wskt obuh"
    smtp_server = "smtp.gmail.com"
    
   # creating the message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    
  # attach the message body
    msg.attach(MIMEText(message, 'plain'))
    
#setting up the smtp connection 

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())

def send_welcome_email(customer_email):
    subject = "Welcome to our Pharmacy Store"
    message_body = f"Dear {customer_email},\n\n\nWelcome to our Pharmacy Store. We are glad to have you on board. We hope you have a great experience with us.\n"
            
    send_email_notification(customer_email, subject, message_body)




# st here refers to streamlit
# '''
# defines the main function for the admin 
# section of the system
# '''

def admin():
    st.title("Pharmacy Database Dashboard")
    menu = ["Drugs", "Customers", "Orders", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Drugs":
        choice = st.sidebar.selectbox("Menu", ["Add", "View", "Update", "Delete"])
        if choice == "Add":
            st.subheader("Add Drugs")

            col1, col2, col3 = st.columns(3)
            with col1:
                drug_name = st.text_area("Enter the Drug Name")
                drug_expiry = st.date_input("Expiry Date of Drug (YYYY-MM-DD)")
                drug_mainuse = st.text_area("When to Use")
            with col2:
                drug_quantity = st.text_area("Enter the quantity")
                drug_price = st.text_area("Enter the price")
                drug_id = st.text_area("Enter the Drug id (example:#D1)")
            with col3:
                uploaded_image = st.file_uploader("Upload Drug Image", type=['png', 'jpg', 'jpeg'])
            if st.button("Add Drug"):
                if uploaded_image:
                    image_path = os.path.join(IMAGES_FOLDER, f"{drug_id}_{drug_name}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.read())
                else:
                    image_path = None
                    
                add_drug_data(drug_name, drug_expiry, drug_mainuse, drug_quantity,drug_price, drug_id,image_path)
                st.success("Successfully Added Data")

        if choice == "View":
            st.subheader("Drug Details")
            drug_result = view_all_drug_data()
            with st.expander("View All Drug Data"):
                drug_clean_df = pd.DataFrame(drug_result, columns=["Name", "Expiry Date", "Use", "Quantity", "ID"])
                st.dataframe(drug_clean_df)

            with st.expander("View Drug Quantity"):
                drug_name_quantity_df = drug_clean_df[['Name', 'Quantity']]
                st.dataframe(drug_name_quantity_df)

        if choice == 'Update':
            st.subheader("Update Drug Details")
            d_id = st.text_area("Drug ID")
            d_use = st.text_area("Drug Use")
            if st.button(label='Update'):
                update_drug(d_use, d_id)

        if choice == 'Delete':
            st.subheader("Delete Drugs")
            did = st.text_area("Drug ID")
            if st.button(label="Delete"):
                delete_drug(did)

    elif choice == "Customers":
        choice = st.sidebar.selectbox("Menu", ["View", "Update", "Delete"])
        if choice == "View":
            st.subheader("Customer Details")
            cust_result = view_all_customer_data()
            with st.expander("View All Customer Data"):
                cust_clean_df = pd.DataFrame(cust_result, columns=["Name", "Password", "Email-ID", "Area", "Number"])
                st.dataframe(cust_clean_df)

        if choice == 'Update':
            st.subheader("Update Customer Details")
            cust_email = st.text_area("Email")
            cust_number = st.text_area("Phone Number")
            if st.button(label='Update'):
                update_customer(cust_email, cust_number)

        if choice == 'Delete':
            st.subheader("Delete Customer")
            cust_email = st.text_area("Email")
            if st.button(label="Delete"):
                delete_customer(cust_email)

    elif choice == "Orders":
        choice = st.sidebar.selectbox("Menu", ["View"])
        if choice == "View":
            st.subheader("Order Details")
            order_result = view_all_order_data()
            with st.expander("View All Order Data"):
                order_clean_df = pd.DataFrame(order_result, columns=["Name", "Items", "Qty", "ID"])
                st.dataframe(order_clean_df)

    elif choice == "About":
        st.subheader("DBMS Mini Project")
        st.subheader("By Indrranil  (38) & Eshan (41)")


#1-> Retrives password from the given username[c_name]
def authenticate(username, password):
    c.execute('SELECT C_Password FROM Customers WHERE C_Name = ?', (username,))
# Fetches result of the sql query, list of tuples(passwprds)
    cust_password = c.fetchall()
# Compares the pass retrived from db with the provided pass 
    return cust_password[0][0] == password


def customer(username, password):
    if authenticate(username, password):
        st.title("Welcome to Pharmacy Store")
        st.subheader("Your Order Details")
        order_result = view_order_data(username)

        with st.expander("View All Order Data"):
            order_clean_df = pd.DataFrame(order_result, columns=["Name", "Items", "Qty", "Price", "ID"])    #define price in each drug below 
            st.dataframe(order_clean_df)

        drug_result = view_all_drug_data()
        st.subheader(f"Drug: {drug_result[0][0]}")
        img_path = os.path.join(os.path.dirname(__file__), 'images/dolo650.jpeg')
        img = Image.open(img_path)
        st.image(img, width=100, caption="Rs. 15/-")
        dolo650 = st.slider(label="Quantity", min_value=0, max_value=5, key=1)
        st.info(f"When to USE: {drug_result[0][2]}")

        st.subheader(f"Drug: {drug_result[1][0]}")
        img_path = os.path.join(os.path.dirname(__file__), 'images/strepsils.jpeg')
        img = Image.open(img_path)
        st.image(img, width=100, caption="Rs. 10/-")
        strepsils = st.slider(label="Quantity", min_value=0, max_value=5, key=2)
        st.info(f"When to USE: {drug_result[1][2]}")

        st.subheader(f"Drug: {drug_result[2][0]}")
        img_path = os.path.join(os.path.dirname(__file__), 'images/vicks.jpeg')
        img = Image.open(img_path)
        st.image(img, width=100, caption="Rs. 65/-")
        vicks = st.slider(label="Quantity", min_value=0, max_value=5, key=3)
        st.info(f"When to USE: {drug_result[2][2]}")
        if st.button(label="Buy now"):
            O_items = ""

            if dolo650 > 0:
                O_items += "Dolo-650,"
            if strepsils > 0:
                O_items += "Strepsils,"
            if vicks > 0:
                O_items += "Vicks"
            O_Qty = f"{dolo650},{strepsils},{vicks}"


            #cal;culates the total price of the order
            O_TotalPrice = calculate_total_price(O_items, O_Qty)
            
            O_id = f"{username}#O{random.randint(0, 1000000)}"
            add_order_data(username, O_items, O_Qty, O_TotalPrice, O_id)


if __name__ == '__main__':
    create_drug_table()
    create_customer_table()
    create_order_table()

    menu = ["Login", "SignUp", "Admin"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox(label="Login"):
            customer(username, password)

    elif choice == "SignUp":
        st.subheader("Create New Account")
        cust_name = st.text_input("Name")
        cust_password = st.text_input("Password", type='password', key=1000)
        cust_password1 = st.text_input("Confirm Password", type='password', key=1001)

        col1, col2, col3 = st.columns(3)
        with col1:
            cust_email = st.text_area("Email ID")
        with col2:
            cust_area = st.text_area("State")
        with col3:
            cust_number = st.text_area("Phone Number")

        if st.button("Signup"):
            if cust_password == cust_password1:
                add_customer_data(cust_name, cust_password, cust_email, cust_area, cust_number)
                st.success("Account Created!")
                st.info("Go to Login Menu to login")
            else:
                st.warning('Password doesn\'t match')

    elif choice == "Admin":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if username == 'admin' and password == 'admin':
            admin()


page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background-color: #3e5162;
opacity: 0.7;
background-image:  radial-gradient(#0020ff 2px, transparent 2px), radial-gradient(#0020ff 2px, #3e5162 2px);
background-size: 80px 80px;
background-position: 0 0,40px 40px;
}
[data-testid="stSidebar"]{
    background-color: #3e5162;
opacity: 0.7;
background-image:  radial-gradient(#0020ff 2px, transparent 2px), radial-gradient(#0020ff 2px, #3e5162 2px);
background-size: 80px 80px;
background-position: 0 0,40px 40px;
    
}
</style>

"""
st.markdown(page_bg_img, unsafe_allow_html=True)