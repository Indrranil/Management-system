from modules.database import c
import stripe
import streamlit as st
from streamlit.components.v1 import components


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