import plotly.express as px
import streamlit as st
import sqlite3

conn = sqlite3.connect("drug_data.db", check_same_thread=False)
c = conn.cursor()



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
            tickfont=dict(size=12, color='white'),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
        ),
        yaxis=dict(
            title='Total Sales',
            tickfont=dict(size=12, color='white'),
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