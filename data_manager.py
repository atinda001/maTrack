import pandas as pd
import os
from datetime import datetime, timedelta

class DataManager:
    def __init__(self):
        self.passengers_file = "data/passengers.csv"
        self.expenses_file = "data/expenses.csv"
        self._initialize_files()

    def _initialize_files(self):
        """Initialize CSV files if they don't exist"""
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.passengers_file):
            pd.DataFrame(columns=[
                'name', 'phone', 'origin', 'destination', 'fare', 'journey_date'
            ]).to_csv(self.passengers_file, index=False)

        if not os.path.exists(self.expenses_file):
            pd.DataFrame(columns=[
                'expense_type', 'amount', 'date', 'notes'
            ]).to_csv(self.expenses_file, index=False)

    def add_passenger_journey(self, name, phone, origin, destination, fare, journey_date):
        """Add a new passenger journey"""
        try:
            # Create a new DataFrame with the journey data
            journey = pd.DataFrame({
                'name': [name],
                'phone': [phone],
                'origin': [origin],
                'destination': [destination],
                'fare': [fare],
                'journey_date': [journey_date]
            })

            # If file is empty, write with header, otherwise append without header
            if os.path.getsize(self.passengers_file) == 0:
                journey.to_csv(self.passengers_file, index=False)
            else:
                journey.to_csv(self.passengers_file, mode='a', header=False, index=False)
        except Exception as e:
            raise Exception(f"Error adding passenger journey: {str(e)}")

    def get_passenger_journeys(self):
        """Get all passenger journeys"""
        try:
            if os.path.exists(self.passengers_file) and os.path.getsize(self.passengers_file) > 0:
                return pd.read_csv(self.passengers_file)
            return pd.DataFrame(columns=['name', 'phone', 'origin', 'destination', 'fare', 'journey_date'])
        except Exception as e:
            raise Exception(f"Error reading passenger journeys: {str(e)}")

    def add_expense(self, expense_type, amount, date, notes):
        """Add a new expense"""
        try:
            expense = pd.DataFrame({
                'expense_type': [expense_type],
                'amount': [amount],
                'date': [date],
                'notes': [notes]
            })

            if os.path.getsize(self.expenses_file) == 0:
                expense.to_csv(self.expenses_file, index=False)
            else:
                expense.to_csv(self.expenses_file, mode='a', header=False, index=False)
        except Exception as e:
            raise Exception(f"Error adding expense: {str(e)}")

    def get_expenses(self):
        """Get all expenses"""
        try:
            if os.path.exists(self.expenses_file) and os.path.getsize(self.expenses_file) > 0:
                return pd.read_csv(self.expenses_file)
            return pd.DataFrame(columns=['expense_type', 'amount', 'date', 'notes'])
        except Exception as e:
            raise Exception(f"Error reading expenses: {str(e)}")

    def get_revenue_by_period(self, start_date, end_date, period_type):
        """Get revenue analysis by period (Weekly/Monthly)"""
        try:
            journeys = self.get_passenger_journeys()
            if journeys.empty:
                return pd.DataFrame(columns=['period', 'revenue'])

            journeys['journey_date'] = pd.to_datetime(journeys['journey_date'])
            mask = (journeys['journey_date'].dt.date >= start_date) & \
                   (journeys['journey_date'].dt.date <= end_date)

            filtered_journeys = journeys[mask]

            if period_type == 'Weekly':
                grouped = filtered_journeys.groupby(pd.Grouper(key='journey_date', freq='W-MON'))
            else:  # Monthly
                grouped = filtered_journeys.groupby(pd.Grouper(key='journey_date', freq='M'))

            revenue_data = grouped['fare'].sum().reset_index()
            revenue_data.columns = ['period', 'revenue']
            return revenue_data

        except Exception as e:
            raise Exception(f"Error calculating revenue by period: {str(e)}")

    def get_performance_metrics(self, start_date, end_date, period_type):
        """Get performance metrics for the selected period"""
        try:
            journeys = self.get_passenger_journeys()
            expenses = self.get_expenses()

            if journeys.empty:
                return None

            # Convert dates
            journeys['journey_date'] = pd.to_datetime(journeys['journey_date'])
            expenses['date'] = pd.to_datetime(expenses['date'])

            # Filter by date range
            journey_mask = (journeys['journey_date'].dt.date >= start_date) & \
                          (journeys['journey_date'].dt.date <= end_date)
            expense_mask = (expenses['date'].dt.date >= start_date) & \
                          (expenses['date'].dt.date <= end_date)

            filtered_journeys = journeys[journey_mask]
            filtered_expenses = expenses[expense_mask]

            # Calculate metrics
            total_trips = len(filtered_journeys['journey_date'].unique())
            total_passengers = len(filtered_journeys)
            avg_passengers_per_trip = total_passengers / total_trips if total_trips > 0 else 0
            avg_revenue_per_trip = filtered_journeys['fare'].sum() / total_trips if total_trips > 0 else 0
            total_expenses = filtered_expenses['amount'].sum()

            return {
                'Total Trips': total_trips,
                'Total Passengers': total_passengers,
                'Average Passengers per Trip': round(avg_passengers_per_trip, 2),
                'Average Revenue per Trip': round(avg_revenue_per_trip, 2),
                'Total Expenses': total_expenses
            }

        except Exception as e:
            raise Exception(f"Error calculating performance metrics: {str(e)}")

    def get_daily_revenue(self, start_date, end_date):
        """Get daily revenue between dates"""
        try:
            journeys = self.get_passenger_journeys()
            if not journeys.empty:
                journeys['journey_date'] = pd.to_datetime(journeys['journey_date'])
                mask = (journeys['journey_date'].dt.date >= start_date) & \
                       (journeys['journey_date'].dt.date <= end_date)
                daily = journeys[mask].groupby(journeys['journey_date'].dt.date)['fare'].sum().reset_index()
                daily.columns = ['date', 'revenue']
                return daily
            return pd.DataFrame(columns=['date', 'revenue'])
        except Exception as e:
            raise Exception(f"Error calculating daily revenue: {str(e)}")

    def get_expense_breakdown(self, start_date, end_date):
        """Get expense breakdown between dates"""
        try:
            expenses = self.get_expenses()
            if not expenses.empty:
                expenses['date'] = pd.to_datetime(expenses['date'])
                mask = (expenses['date'].dt.date >= start_date) & \
                       (expenses['date'].dt.date <= end_date)
                return expenses[mask].groupby('expense_type')['amount'].sum().reset_index()
            return pd.DataFrame(columns=['expense_type', 'amount'])
        except Exception as e:
            raise Exception(f"Error calculating expense breakdown: {str(e)}")