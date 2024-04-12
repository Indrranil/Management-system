import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
