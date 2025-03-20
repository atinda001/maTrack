import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from data_manager import DataManager
from utils import validate_phone, calculate_financial_metrics

# Page configuration
st.set_page_config(
    page_title="Transport Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs {
        background-color: #F5F7FA;
        padding: 1rem;
        border-radius: 10px;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stDataFrame"] {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize DataManager
dm = DataManager()

def main():
    st.title("🚌 Transport Management System")

    # Sidebar navigation with icons
    page = st.sidebar.selectbox(
        "Navigation",
        ["🎫 Passenger Journey", "💰 Vehicle Expenses", "📊 Financial Reports"]
    )

    if "🎫 Passenger Journey" in page:
        passenger_journey_page()
    elif "💰 Vehicle Expenses" in page:
        vehicle_expenses_page()
    else:
        financial_reports_page()

def passenger_journey_page():
    st.header("🎫 Record Passenger Journey")

    with st.container():
        st.markdown("""
            <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4>Trip Details</h4>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            journey_date = st.date_input("Journey Date")
        with col2:
            origin = st.text_input("Origin")
        with col3:
            destination = st.text_input("Destination")

        fare = st.number_input("Fare Amount per Passenger", min_value=0.0, step=0.5)

    # Passenger Details Section
    st.markdown("""
        <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
            <h4>Passenger Details</h4>
            <p>Enter details for all 11 passengers:</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state for passenger details
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

    if st.button("Record All Passengers", type="primary"):
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

    # Display recent journeys in a styled container
    st.markdown("""
        <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
            <h4>Recent Journeys</h4>
        </div>
    """, unsafe_allow_html=True)

    journeys = dm.get_passenger_journeys()
    if not journeys.empty:
        st.dataframe(
            journeys.tail(20),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No journeys recorded yet")

def vehicle_expenses_page():
    st.header("💰 Vehicle Expenses")

    with st.container():
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
                <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <h4>Record New Expense</h4>
                </div>
            """, unsafe_allow_html=True)

            expense_type = st.selectbox("Expense Type", ["Fuel", "Maintenance", "Insurance", "Other"])
            amount = st.number_input("Amount", min_value=0.0, step=1.0)
            date = st.date_input("Date")
            notes = st.text_area("Notes")

            if st.button("Record Expense", type="primary"):
                if amount <= 0:
                    st.error("Amount must be greater than 0")
                else:
                    dm.add_expense(expense_type, amount, date, notes)
                    st.success("Expense recorded successfully")
                    st.rerun()

        with col2:
            st.markdown("""
                <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <h4>Recent Expenses</h4>
                </div>
            """, unsafe_allow_html=True)

            expenses = dm.get_expenses()
            if not expenses.empty:
                st.dataframe(
                    expenses.tail(10),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No expenses recorded yet")

def financial_reports_page():
    st.header("📊 Financial Reports")

    with st.container():
        # Time frame selector
        st.markdown("""
            <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4>Select Analysis Period</h4>
            </div>
        """, unsafe_allow_html=True)

        analysis_type = st.selectbox(
            "Analysis Type",
            ["Trip-based", "Weekly", "Monthly"]
        )

        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            if analysis_type == "Trip-based":
                start_date = st.date_input("Select Trip Date")
                end_date = start_date
            else:
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            if analysis_type != "Trip-based":
                end_date = st.date_input("End Date", datetime.now())

        if start_date > end_date:
            st.error("Start date must be before end date")
            return

        # Calculate metrics
        metrics = calculate_financial_metrics(dm, start_date, end_date, analysis_type)

        # Display metrics in a styled container
        st.markdown("""
            <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                <h4>Financial Overview</h4>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Revenue", f"${metrics['total_revenue']:.2f}")
        col2.metric("Total Expenses", f"${metrics['total_expenses']:.2f}")
        col3.metric("Net Profit", f"${metrics['net_profit']:.2f}")
        if analysis_type == "Trip-based":
            col4.metric("Passengers", metrics['passenger_count'])

        # Revenue chart
        if analysis_type != "Trip-based":
            st.markdown("""
                <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                    <h4>Revenue Trend</h4>
                </div>
            """, unsafe_allow_html=True)

            revenue_data = dm.get_revenue_by_period(start_date, end_date, analysis_type)
            if not revenue_data.empty:
                fig = px.line(
                    revenue_data,
                    x='period',
                    y='revenue',
                    title=f'{analysis_type} Revenue Analysis'
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=40, l=0, r=0, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)

        # Expense breakdown
        st.markdown("""
            <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                <h4>Expense Breakdown</h4>
            </div>
        """, unsafe_allow_html=True)

        expense_breakdown = dm.get_expense_breakdown(start_date, end_date)
        if not expense_breakdown.empty:
            fig = px.pie(
                expense_breakdown,
                values='amount',
                names='expense_type',
                title='Expense Distribution'
            )
            fig.update_layout(
                showlegend=True,
                margin=dict(t=40, l=0, r=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Additional analysis
        if analysis_type != "Trip-based":
            st.markdown("""
                <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                    <h4>Performance Metrics</h4>
                </div>
            """, unsafe_allow_html=True)

            performance = dm.get_performance_metrics(start_date, end_date, analysis_type)
            if performance:
                metrics_df = pd.DataFrame([performance])
                st.dataframe(
                    metrics_df,
                    use_container_width=True,
                    hide_index=True
                )

if __name__ == "__main__":
    main()