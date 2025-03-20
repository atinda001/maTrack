import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from data_manager import DataManager
from utils import validate_phone, calculate_financial_metrics
from auth_manager import AuthManager

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

# Initialize managers
auth_manager = AuthManager()
dm = DataManager()

def login_page():
    st.title("🚌 Transport Management System")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                success, message = auth_manager.login_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.divider()
        if st.button("Login with Google"):
            # Google OAuth implementation will go here
            pass

    with tab2:
        with st.form("register_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")

            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = auth_manager.register_user(email, password, name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        login_page()
        return

    st.title("🚌 Transport Management System")

    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        auth_manager.logout_user()
        st.session_state.authenticated = False
        st.rerun()

    # Navigation
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

    # Trip Details Section
    with st.container():
        st.markdown("""
            <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4>Trip Details</h4>
            </div>
        """, unsafe_allow_html=True)

        # Initialize session state for trip details
        if 'current_journey' not in st.session_state:
            st.session_state.current_journey = {
                'date': None,
                'origin': '',
                'destination': '',
                'fare': 0.0,
                'passengers': []
            }

        col1, col2, col3 = st.columns(3)
        with col1:
            journey_date = st.date_input("Journey Date")
            st.session_state.current_journey['date'] = journey_date
        with col2:
            origin = st.text_input("Origin")
            st.session_state.current_journey['origin'] = origin
        with col3:
            destination = st.text_input("Destination")
            st.session_state.current_journey['destination'] = destination

        fare = st.number_input("Fare Amount per Passenger", min_value=0.0, step=0.5)
        st.session_state.current_journey['fare'] = fare

    # Passenger Details Section
    st.markdown("""
        <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
            <h4>Add Passenger</h4>
            <p>Add passengers one by one (Maximum: 11 passengers)</p>
        </div>
    """, unsafe_allow_html=True)

    # Display current passenger count
    passenger_count = len(st.session_state.current_journey['passengers'])
    st.info(f"Passengers added: {passenger_count}/11")

    # Add single passenger form
    if passenger_count < 11:
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Passenger Name", key="new_passenger_name")
        with col2:
            phone = st.text_input("Phone Number", key="new_passenger_phone")

        if st.button("Add Passenger", type="primary", disabled=passenger_count >= 11):
            # Validate inputs
            errors = []
            if not name:
                errors.append("Name is required")
            if not phone:
                errors.append("Phone number is required")
            elif not validate_phone(phone):
                errors.append("Invalid phone number format")

            if not errors:
                try:
                    # Add passenger to the journey
                    dm.add_passenger_journey(
                        name=name,
                        phone=phone,
                        origin=origin,
                        destination=destination,
                        fare=fare,
                        journey_date=journey_date
                    )

                    # Add to current journey list
                    st.session_state.current_journey['passengers'].append({
                        'name': name,
                        'phone': phone
                    })

                    st.success(f"Passenger {name} added successfully!")

                    # Clear the input fields
                    st.session_state.new_passenger_name = ""
                    st.session_state.new_passenger_phone = ""

                    if len(st.session_state.current_journey['passengers']) >= 11:
                        st.success("Maximum number of passengers reached!")

                    st.rerun()
                except Exception as e:
                    st.error("Error adding passenger. Please try again.")
            else:
                for error in errors:
                    st.error(error)

    # Display current journey passengers
    if st.session_state.current_journey['passengers']:
        st.markdown("""
            <div style='background-color: #F5F7FA; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                <h4>Current Journey Passengers</h4>
            </div>
        """, unsafe_allow_html=True)

        passengers_df = pd.DataFrame(st.session_state.current_journey['passengers'])
        st.dataframe(passengers_df, use_container_width=True, hide_index=True)

        if st.button("Clear Current Journey", type="secondary"):
            st.session_state.current_journey = {
                'date': None,
                'origin': '',
                'destination': '',
                'fare': 0.0,
                'passengers': []
            }
            st.rerun()

    # Display all recent journeys
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
            hide_index=True
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