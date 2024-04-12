
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
from st_paywall import add_auth
import stripe
import streamlit.components.v1 as components
import plotly.express as px
import webbrowser

stripe.api_key = "sk_test_51OubhsSAkfFPs5lWOLSJwE6IE7gBhEgGQNkiSPWAP7NQr3JotPH3iXJEmQ0ojXfBUdnLpFD5qEo7xI74IV3cKfES00QXSQYpoM"
#stripe.SetupIntent.create(usage="on_session")
payment_url = "https://buy.stripe.com/test_3cs8xIc0S4Kk9I47ss"


# IMAGES_FOLDER = "images"

# sets up connection with the database
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
                 (D_Name, D_Expdate, D_Use, D_Qty, D_Price, D_id,D_image_path)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (Dname, Dexpdate, Duse, Dqty, DPrice, Did, image_path))
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
    # Add this line to check the drug name
    print("Fetching price for drug:", drug_name)
    result = c.execute(
        'SELECT D_Price FROM Drugs WHERE D_Name = ?',
        (drug_name,)
    ).fetchone()
    # Add this line to check the result from the database
    print("Result from database:", result)
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
    c.execute('''
        INSERT INTO Sales (Date, TotalPrice)
        VALUES (DATE(), ?)
        ''', (O_TotalPrice,))
    conn.commit()

    # Refresh sales trend graph
    visualize_sales_trends()


def view_order_data(customer_name):
    return c.execute(
        'SELECT * FROM Orders WHERE O_Name = ?',
        (customer_name,)
    ).fetchall()


def view_all_order_data():
    return c.execute('SELECT * FROM Orders').fetchall()


# email notificatin code

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

# setting up the smtp connection

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
    IMAGES_FOLDER = "images"
    st.title("Pharmacy Database Dashboard")
    menu = ["Drugs", "Customers", "Orders", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Drugs":
        choice = st.sidebar.selectbox(
            "Menu", ["Add", "View", "Update", "Delete"])
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
                uploaded_image = st.file_uploader(
                    "Upload Drug Image", type=['png', 'jpg', 'jpeg'])
            if st.button("Add Drug"):
                if uploaded_image:
                    image_path = os.path.join(
                        IMAGES_FOLDER, f"{drug_id}_{drug_name}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.read())
                else:
                    image_path = None

                add_drug_data(drug_name, drug_expiry, drug_mainuse,  drug_quantity, drug_id, drug_price, image_path)
                st.success("Successfully Added Data")

        if choice == "View":
            st.subheader("Drug Details")
            drug_result = view_all_drug_data()
            with st.expander("View All Drug Data"):
                drug_clean_df = pd.DataFrame(
                    drug_result, columns=["Name", "Expiry_Date", "Use", "Quantity", "ID", "Price"])
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
                cust_clean_df = pd.DataFrame(
                    cust_result, columns=["Name", "Password", "Email-ID", "Area", "Number"])
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
                order_clean_df = pd.DataFrame(
                    order_result, columns=["Name", "Items", "Qty", "ID", "Price"])
                st.dataframe(order_clean_df)

    elif choice == "About":
        st.subheader("Python Project")
        st.subheader("By Indrranil ")


# 1-> Retrives password from the given username[c_name]
def authenticate(username, password):
    c.execute('SELECT C_Password FROM Customers WHERE C_Name = ?', (username,))
# Fetches result of the sql query, list of tuples(passwprds)
    cust_password = c.fetchall()
# Compares the pass retrived from db with the provided pass
    return cust_password[0][0] == password

def retrieve_customer_email(username):
    c.execute("SELECT C_Email FROM Customers WHERE C_Name = ?", (username,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None

def fetch_order_details(username):
    c.execute("SELECT O_Items, O_Qty FROM Orders WHERE O_Name = ?", (username,))
    result = c.fetchone()
    if result:
        return result
    else:
        return None
##fix the email, send only the send_purchase_confirmation_email wala mail and fic the checkout
#def checkout(username, O_TotalPrice):
    try:
        # Create a PaymentIntent to initiate the payment process
        intent = stripe.PaymentIntent.create(
            amount=int(O_TotalPrice * 100),  # Amount in cents
            currency="inr",
            description="Pharmacy Order",
            metadata={"order_id": username},
        )
        # Redirect the user to the Stripe payment page
        st.markdown("**Redirecting to Stripe payment page...**")
        st.write(f"**Amount: Rs. {O_TotalPrice:.2f}**")
        st.markdown(f"**PaymentIntent Client Secret:** {intent.client_secret}")
        html_redirect = f"""
        <script type="text/javascript">
        window.location.href = "https://checkout.stripe.com/pay/{intent.client_secret}";
        </script>
        """
        components.html(html_redirect)
    except stripe.error.StripeError as e:
        st.error(f"Error processing payment: {e}")
def checkout(username, O_TotalPrice):
#def checkout(username, O_TotalPrice):
    try:
        # Redirect the user to the payment page in the default web browser
        webbrowser.open_new_tab(payment_url)

        # Send purchase confirmation email
        customer_email = retrieve_customer_email(username)
        if customer_email:
            # Fetch the details of the drugs bought
            order_details = fetch_order_details(username)
            if order_details:
                items_table = "<table border='1'><tr><th>Drug Name</th><th>Quantity</th></tr>"
                for item in order_details:
                    items_table += f"<tr><td>{item[0]}</td><td>{item[1]}</td></tr>"
                items_table += "</table>"
                subject = "Purchase Confirmation"
                message_body = f"Dear {username},\n\nThank you for your purchase. Below are the details of your order:\n\n{items_table}\n\nTotal Price: Rs. {O_TotalPrice:.2f}\n\nThank you for shopping with us!"
                send_email_notification(customer_email, subject, message_body)
    except Exception as e:
        st.error(f"Error processing purchase and sending email: {e}")

    try:
        # Redirect the user to the payment page in the default web browser
        webbrowser.open_new_tab(payment_url)
    except Exception as e:
        st.error(f"Error redirecting to payment page: {e}")


def send_purchase_confirmation_email(customer_email, order_items, order_total_price):
    # Construct the email message
    message = f"Dear {customer_email},\n\n"
    message += "Thank you for your purchase. Below are the details of your order:\n\n"

    # Add order items to the message
    message += "Drug Name\tQuantity\n"
    for item, quantity in order_items:
        message += f"{item}\t\t{quantity}\n"
    message += f"\nTotal Price: Rs. {order_total_price:.2f}\n\n"

    # Create a heart pattern
    heart = "❤️"
    heart_pattern = (
        f" {heart}     {heart} \n"
        f"{heart} {heart} {heart} {heart} {heart}\n"
        f"  {heart} {heart}  \n"
        f"    {heart}    "
    )
    message += f"{heart_pattern}\n\n"

    # Add a thank you message
    message += "Thank you for shopping with us!\n"

    # Send the email
    send_email_notification(customer_email, "Purchase Confirmation", message,heart)







def retrive_password(username):
    c.execute("SELECT  C_Password FROM Customers WHERE C_Name = ?", (username,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None

def forgot_password(username):
    st.subheader("Forgot Password")
    username = st.text_input("User Name")
    if st.tk.Button("Retrieve Button"):
        password = retrive_password(username)
        if password:
            st.success(f"Your password is {password}")
        else:
            st.error("No such user exists in the database. Please check the username and try again.")

def retrieve_username(email):
    c.execute("SELECT C_Name FROM Customers WHERE C_Email = ?", (email,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None

def create_payment_intent(amount):
    try:
        # Create a PaymentIntent to initiate the payment process
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in cents
            currency="INR",  # Currency
            description="Pharmacy Order",  # Description of the payment
            metadata={"order_id": "your_order_id"},  # Metadata for tracking purposes
        )
        return intent.client_secret
    except stripe.error.StripeError as e:
        # Handle any errors that occur during the payment process
        st.error(f"Error processing payment: {e}")

# Define a function to redirect the user to the Stripe payment page
def redirect_to_stripe_payment(client_secret):
    st.markdown("**Redirecting to Stripe payment page...**")
    html_redirect = f"""
    <script type="text/javascript">
    window.location.href = "https://checkout.stripe.com/pay/{client_secret}";
    </script>
    """
    components.html(html_redirect)





# Add this function to your project to fetch sales data
def fetch_sales_data():
    # Assuming you have a Sales table with columns Date and TotalPrice
    sales_data = c.execute("SELECT Date, TotalPrice FROM Sales").fetchall()
    return sales_data

# Add this function to your project to visualize sales trends


def visualize_sales_trends():
    # Fetch sales data from the database
    sales_data = fetch_sales_data()

    # Extract dates and total prices from sales data
    dates = [row[0] for row in sales_data]
    total_prices = [row[1] for row in sales_data]

    # Create a Plotly figure using Plotly Express
    fig = px.line(x=dates, y=total_prices, title='Sales Trends', labels={'x': 'Date', 'y': 'Total Sales'})

    fig.update_traces(line=dict(color='yellow'))

    # Customize the figure layout to only display x-axis and y-axis
    fig.update_layout(
        xaxis=dict(
            title='Date',
            tickfont=dict(size=12, color='black'),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
        ),
        yaxis=dict(
            title='Total Sales',
            tickfont=dict(size=12, color='black'),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
        ),
        showlegend=False,  # Disable legend
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    # Display the Plotly figure using Streamlit
    st.plotly_chart(fig)

# match O_items names

def customer(username, password):
    if authenticate(username, password):
        st.title("Welcome to Pharmacy Store")
        st.subheader("Your Order Details")
        order_result = view_order_data(username)

        with st.expander("View All Order Data"):
            order_clean_df = pd.DataFrame(order_result, columns=[ "Name", "Items", "Qty", "ID", "Price"])  # define price in each drug below
            st.dataframe(order_clean_df)

        drug_result = view_all_drug_data()
        st.subheader(f"Drug: {drug_result[0][0]}")
        img_path = os.path.join(os.path.dirname(
            __file__), 'images/dolo650.jpeg')
        img = Image.open(img_path)
        st.image(img, width=100, caption=f"Rs. {fetch_drug_price(drug_result[0][0]):.2f}/-")
        dolo650 = st.slider(label="Quantity", min_value=0, max_value=5, key=1)
        st.info(f"When to USE: {drug_result[0][2]}")

        st.subheader(f"Drug: {drug_result[1][0]}")
        img_path = os.path.join(os.path.dirname(
            __file__), 'images/strepsils.jpeg')
        img = Image.open(img_path)
        st.image(img, width=100, caption=f"Rs. {fetch_drug_price(drug_result[1][0]):.2f}/-")
        strepsils = st.slider(
            label="Quantity", min_value=0, max_value=5, key=2)
        st.info(f"When to USE: {drug_result[1][2]}")

        st.subheader(f"Drug: {drug_result[2][0]}")
        img_path = os.path.join(os.path.dirname(__file__), 'images/vicks.jpeg')
        img = Image.open(img_path)
        st.image(img, width=100, caption=f"Rs. { fetch_drug_price(drug_result[2][0]):.2f}/-")
        vicks = st.slider(label="Quantity", min_value=0, max_value=5, key=3)
        st.info(f"When to USE: {drug_result[2][2]}")
        O_TotalPrice = 0
        O_id = ""
        if st.button(label="Buy now"):
            O_items = ""

            if dolo650 > 0:
                O_items += "Dolo 650,"
            if strepsils > 0:
                O_items += "Strapsils,"
            if vicks > 0:
                O_items += "Vicks VaporRub"
            O_Qty = f"{dolo650},{strepsils},{vicks}"

            # calculates the total price of the order
            O_TotalPrice = calculate_total_price(O_items, O_Qty)

            st.success(f"Total Price: Rs. {O_TotalPrice:.2f}")

            O_id = f"{username}#O{random.randint(0, 1000000)}"
            add_order_data(username, O_items,  O_Qty, O_TotalPrice, O_id)

            checkout(username, O_TotalPrice)


    else:
        st.error("Authentication failed. Please check your username and password.")




if __name__ == '__main__':
    create_drug_table()
    create_customer_table()
    create_order_table()

    menu = ["Login", "SignUp", "Admin", "About","Sales Trends"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox(label="Login"):
            customer(username, password)

    if st.button("Retrieve Password"):
        username = st.text_input("Enter your User Name")
        password = retrive_password(username)
        if password:
            st.success(f"Your password is {password}")
        else:
            st.error("No such user exists in the database. Please check the username and try again.")

    if st.button("Retrieve Username"):
        email = st.text_input("Enter your email address")
        username = retrieve_username(email)
        if username:
            st.success(f"Your username is {username}")
        else:
            st.error("No user found with this email address.")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        cust_name = st.text_input("Name")
        cust_password = st.text_input("Password", type='password', key=1000)
        cust_password1 = st.text_input(
            "Confirm Password", type='password', key=1001)

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

        add_auth(True)
        st.error("You need to login to access this page")

    elif choice == "About":
        st.subheader("Python Project")
        st.subheader("By Indrranil")

    elif choice == "Admin":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if username == 'admin' and password == 'admin':
            admin()
            visualize_sales_trends()

    elif choice == "Sales Trends":
        st.subheader("Sales Trends")
        visualize_sales_trends()



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


# demo commnet
