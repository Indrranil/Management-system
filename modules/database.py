import sqlite3
from modules.email import send_welcome_email



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
