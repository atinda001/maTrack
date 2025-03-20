import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from data_manager import DataManager
from utils import validate_phone, calculate_financial_metrics

st.set_page_config(page_title="Transport Management System", layout="wide")

# Initialize DataManager
dm = DataManager()

def main():
    st.title("Transport Management System")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Passenger Journey", "Vehicle Expenses", "Financial Reports"]
    )

    if page == "Passenger Journey":
        passenger_journey_page()
    elif page == "Vehicle Expenses":
        vehicle_expenses_page()
    else:
        financial_reports_page()

def passenger_journey_page():
    st.header("Record Passenger Journey")

    # Common journey details
    journey_date = st.date_input("Journey Date")
    origin = st.text_input("Origin")
    destination = st.text_input("Destination")
    fare = st.number_input("Fare Amount per Passenger", min_value=0.0, step=0.5)

    # Create a form for 11 passengers
    st.subheader("Passenger Details")
    st.write("Enter details for all 11 passengers:")

    # Initialize session state for passenger details if not exists
    if 'passengers' not in st.session_state:
        st.session_state.passengers = [{"name": "", "phone": ""} for _ in range(11)]

    # Create columns for the table header
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.write("Passenger #")
    with col2:
        st.write("Name")
    with col3:
        st.write("Phone Number")

    # Create input fields for each passenger
    for i in range(11):
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.write(f"{i + 1}")
        with col2:
            st.session_state.passengers[i]["name"] = st.text_input(
                f"Name {i+1}",
                key=f"name_{i}",
                value=st.session_state.passengers[i]["name"]
            )
        with col3:
            st.session_state.passengers[i]["phone"] = st.text_input(
                f"Phone {i+1}",
                key=f"phone_{i}",
                value=st.session_state.passengers[i]["phone"]
            )

    if st.button("Record All Passengers"):
        # Validate inputs
        errors = []
        if not origin or not destination:
            errors.append("Origin and destination are required")
        if fare <= 0:
            errors.append("Fare amount must be greater than 0")

        # Validate passenger details
        valid_passengers = []
        for i, passenger in enumerate(st.session_state.passengers):
            if passenger["name"] or passenger["phone"]:  # If either field is filled
                if not passenger["name"]:
                    errors.append(f"Name is required for passenger {i+1}")
                elif not passenger["phone"]:
                    errors.append(f"Phone number is required for passenger {i+1}")
                elif not validate_phone(passenger["phone"]):
                    errors.append(f"Invalid phone number for passenger {i+1}")
                else:
                    valid_passengers.append(passenger)

        if len(valid_passengers) == 0:
            errors.append("At least one passenger must be added")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Add journey for each valid passenger
            for passenger in valid_passengers:
                dm.add_passenger_journey(
                    passenger["name"],
                    passenger["phone"],
                    origin,
                    destination,
                    fare,
                    journey_date
                )
            st.success(f"Journey recorded successfully for {len(valid_passengers)} passengers")
            # Clear the form
            st.session_state.passengers = [{"name": "", "phone": ""} for _ in range(11)]
            st.rerun()

    # Display recent journeys
    st.subheader("Recent Journeys")
    journeys = dm.get_passenger_journeys()
    if not journeys.empty:
        st.dataframe(journeys.tail(20))
    else:
        st.info("No journeys recorded yet")

def vehicle_expenses_page():
    st.header("Vehicle Expenses")

    col1, col2 = st.columns(2)

    with col1:
        expense_type = st.selectbox("Expense Type", ["Fuel", "Maintenance", "Insurance", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        date = st.date_input("Date")
        notes = st.text_area("Notes")

        if st.button("Record Expense"):
            if amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                dm.add_expense(expense_type, amount, date, notes)
                st.success("Expense recorded successfully")
                st.rerun()

    with col2:
        st.subheader("Recent Expenses")
        expenses = dm.get_expenses()
        if not expenses.empty:
            st.dataframe(expenses.tail(10))
        else:
            st.info("No expenses recorded yet")

def financial_reports_page():
    st.header("Financial Reports")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    if start_date > end_date:
        st.error("Start date must be before end date")
        return

    # Calculate metrics
    metrics = calculate_financial_metrics(dm, start_date, end_date)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${metrics['total_revenue']:.2f}")
    col2.metric("Total Expenses", f"${metrics['total_expenses']:.2f}")
    col3.metric("Net Profit", f"${metrics['net_profit']:.2f}")

    # Revenue chart
    st.subheader("Daily Revenue")
    daily_revenue = dm.get_daily_revenue(start_date, end_date)
    if not daily_revenue.empty:
        fig = px.line(daily_revenue, x='date', y='revenue', title='Daily Revenue')
        st.plotly_chart(fig)

    # Expense breakdown
    st.subheader("Expense Breakdown")
    expense_breakdown = dm.get_expense_breakdown(start_date, end_date)
    if not expense_breakdown.empty:
        fig = px.pie(expense_breakdown, values='amount', names='expense_type', title='Expense Distribution')
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()