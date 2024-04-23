
# import commands below download a few python libs

from modules.authentication import (
    authenticate,
    retrieve_customer_email,
    fetch_order_details,
    send_purchase_confirmation_email,
    retrive_password,
    forgot_password,
    retrieve_username,
)

import os
import random
import requests
from PIL import Image
import streamlit as st
import stripe
import sqlite3
from modules.email import send_welcome_email, send_purchase_confirmation_email
from modules.stripe import (
    checkout
)
from modules.email import send_email_notification
from modules.trends import visualize_sales_trends
import pandas as pd
from modules.database import(
    create_customer_table,
    add_customer_data,
    view_all_customer_data,
    update_customer,
    delete_customer,
    create_drug_table,
    add_drug_data,
    view_all_drug_data,
    create_order_table,
    delete_order,
    fetch_drug_price,
    view_order_data,
    add_order_data,
    calculate_total_price,
    update_drug,
    delete_drug,
    view_all_order_data
)

from streamlit import selectbox
from st_paywall import add_auth
from streamlit_lottie import st_lottie



stripe.api_key = "sk_test_51OubhsSAkfFPs5lWOLSJwE6IE7gBhEgGQNkiSPWAP7NQr3JotPH3iXJEmQ0ojXfBUdnLpFD5qEo7xI74IV3cKfES00QXSQYpoM"
#stripe.SetupIntent.create(usage="on_session")
payment_url = "https://buy.stripe.com/test_3cs8xIc0S4Kk9I47ss"




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

                add_drug_data(drug_name, drug_expiry, drug_mainuse, drug_quantity, drug_price, drug_id, image_path)
                st.success("Successfully Added Data")

        if choice == "View":
            st.subheader("Drug Details")
            drug_result = view_all_drug_data()
            with st.expander("View All Drug Data"):
                drug_clean_df = pd.DataFrame(
                    drug_result, columns=["Name", "Expiry_Date", "Use", "Quantity", "Price", "ID", "Image"])
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



# Modify the function to fetch latest drug data from the database
def customer(username, password):
    if authenticate(username, password):
        st.title("Welcome to Pharmacy Store")
        st.subheader("Your Order Details")
        order_result = view_order_data(username)

        with st.expander("View All Order Data"):
            order_clean_df = pd.DataFrame(order_result, columns=["Name", "Items", "Qty", "ID", "Price"])
            st.dataframe(order_clean_df)

        # Fetch latest drug data from the database
        drug_result = view_all_drug_data()
        for drug_info in drug_result:
            # Extract drug name from the tuple
            drug_name = drug_info[0]
            st.subheader(f"Drug: {drug_name}")
            img_path = os.path.join(os.path.dirname(__file__), f'images/{drug_name}.jpeg')
            img = Image.open(img_path)
            price = float(drug_info[5])
            st.image(img, width=100, caption=f"Rs. {price:.2f}/-")
            quantity = st.slider(label="Quantity", min_value=0, max_value=5, key=drug_name)
            st.info(f"When to USE: {drug_info[2]}")

        # Process order
        if st.button(label="Buy now"):
            total_price = calculate_total_price(drug_result, username)
            st.success(f"Total Price: Rs. {total_price:.2f}")

            order_items = ", ".join([f"{info[0]} x{st.session_state[info[0]]}" for info in drug_result if st.session_state[info[0]] > 0])
            order_quantity = ", ".join([str(st.session_state[info[0]]) for info in drug_result if st.session_state[info[0]] > 0])

            order_id = f"{username}#O{random.randint(0, 1000000)}"
            add_order_data(username, order_items, order_quantity, total_price, order_id)

            checkout(username, total_price)
    else:
        st.error("Authentication failed. Please check your username and password.")




url = 'https://lottie.host/2b89cf80-72e9-42ec-95e6-97ffd72bba14/UX6EOmiR3Q.json'
success_tick_url = "https://lottie.host/353e41f1-6210-4d77-921d-74123030d22a/yYxAX857tH.json"
animation_played = False

def play_animation(url):
    st_lottie(url, width=400, height=400, speed=2, key='animation')

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
    if choice == "Login" and st.sidebar.button("Retrieve Password"):
        username = st.text_input("Enter your User Name")
        password = retrive_password(username)
        if password:
            st.success(f"Your password is {password}")
        else:
            st.error("No such user exists in the database. Please check the username and try again.")

    if choice == "Login" and st.sidebar.button("Retrieve Username"):
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

        #add_auth(True)
        #st.error("You need to login to access this page")

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


#page_bg_img = """
#<style>
#[data-testid="stAppViewContainer"] {
#background-color: #000000;
#opacity: 1;
#background-image:  linear-gradient(#47e2d5 0.4px, transparent 0.4px), linear-gradient(to right, #47e2d5 0.4px, #000000 0.4px);
#background-size: 8px 8px;
#}

#[data-testid="stSidebar"] {
#background-color: #000000;
#opacity: 1;
#background-image:  linear-gradient(#47e2d5 0.4px, transparent 0.4px), linear-gradient(to right, #47e2d5 0.4px, #000000 0.4px);
#background-size: 8px 8px;
#}
#</style>
#"""
##st.markdown(page_bg_img, unsafe_allow_html=True)
