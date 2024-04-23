from modules.email import send_email_notification
from modules.authentication import retrieve_customer_email, fetch_order_details
import stripe 
import streamlit as st
import webbrowser
from streamlit.components.v1 import components

stripe.api_key = "sk_test_51OubhsSAkfFPs5lWOLSJwE6IE7gBhEgGQNkiSPWAP7NQr3JotPH3iXJEmQ0ojXfBUdnLpFD5qEo7xI74IV3cKfES00QXSQYpoM"
#stripe.SetupIntent.create(usage="on_session")
payment_url = "https://buy.stripe.com/test_3cs8xIc0S4Kk9I47ss"



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
